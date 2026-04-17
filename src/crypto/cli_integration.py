"""
dystopian-crypto SSL CLI — create-ca, create-key, create-csr, vault commands.

Runnable both standalone (``python -m crypto.cli_integration``) and as
importable Click groups that :mod:`manage` can wire into the main
management script.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import click

# ---------------------------------------------------------------------------
# Ensure src/ is on sys.path so ``crypto.*`` imports resolve when run
# directly (``python src/crypto/cli_integration.py``).
# ---------------------------------------------------------------------------
_SRC = Path(__file__).resolve().parent.parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from crypto.key_manager import KeyManager, PasswordManager  # noqa: E402
from crypto.vault import Vault  # noqa: E402


# ===================================================================
# Default key directory — user-writable location
# ===================================================================
_DEFAULT_KEYS_DIR = str(
    Path.home() / ".dystopian-crypto" / "keys"
)


# ===================================================================
# SSL command group
# ===================================================================


@click.group("ssl")
def ssl() -> None:
    """SSL / Ed25519 key management for dystopian infrastructure."""


@ssl.command("create-ca")
@click.option("--name", required=True, help="CA name (e.g. RootCA)")
@click.option(
    "--pass", "password_file", required=True,
    type=click.Path(exists=True),
    help="Path to file containing the CA password",
)
@click.option(
    "--vault-pass", "vault_pass_file", default=None,
    type=click.Path(exists=True),
    help="If given, store password file content in the vault under this master password",
)
@click.option("--overwrite", is_flag=True, help="Overwrite existing keys")
@click.option(
    "--keys-dir", default=_DEFAULT_KEYS_DIR,
    type=click.Path(), help="Output directory for keys",
)
def ssl_create_ca(
    name: str,
    password_file: str,
    vault_pass_file: Optional[str],
    overwrite: bool,
    keys_dir: str,
) -> None:
    """Create a Certificate Authority keypair (Ed25519, password-protected)."""
    try:
        # Optionally stash the password content in the vault.
        if vault_pass_file is not None:
            v = Vault()
            content = Path(password_file).read_text().strip()
            v.store(f"{name}-ca-pass", content, vault_pass_file, overwrite=overwrite)
            click.echo(f"  Vault: stored password as '{name}-ca-pass'")

        km = KeyManager(keys_dir=keys_dir)
        metadata = km.create_ca_keypair(
            name=name,
            password_file=password_file,
            overwrite=overwrite,
        )

        click.secho("✓ CA created successfully", fg="green")
        click.echo(json.dumps(metadata, indent=2))

    except Exception as exc:
        click.secho(f"✗ Error: {exc}", fg="red", err=True)
        raise SystemExit(1)


@ssl.command("create-key")
@click.option("--name", required=True, help="Key name")
@click.option(
    "--pass", "password_file", required=True,
    type=click.Path(exists=True),
    help="Path to password file",
)
@click.option("--ca", "ca_name", default=None, help="Parent CA name (creates signing key)")
@click.option("--overwrite", is_flag=True, help="Overwrite existing keys")
@click.option(
    "--keys-dir", default=_DEFAULT_KEYS_DIR,
    type=click.Path(), help="Output directory for keys",
)
def ssl_create_key(
    name: str,
    password_file: str,
    ca_name: Optional[str],
    overwrite: bool,
    keys_dir: str,
) -> None:
    """Create an Ed25519 keypair — standalone or under a CA."""
    try:
        km = KeyManager(keys_dir=keys_dir)

        if ca_name:
            metadata = km.create_signing_keypair(
                name=name,
                ca_name=ca_name,
                password_file=password_file,
                overwrite=overwrite,
            )
        else:
            metadata = km.create_ca_keypair(
                name=name,
                password_file=password_file,
                overwrite=overwrite,
            )

        click.secho("✓ Key created", fg="green")
        click.echo(json.dumps(metadata, indent=2))

    except Exception as exc:
        click.secho(f"✗ Error: {exc}", fg="red", err=True)
        raise SystemExit(1)


@ssl.command("create-csr")
@click.option("--name", required=True, help="Key / CSR base name")
@click.option(
    "--pass", "password_file", required=True,
    type=click.Path(exists=True),
    help="Path to password file for the private key",
)
@click.option("--common-name", "cn", required=True, help="Subject Common Name (CN)")
@click.option("--org", default=None, help="Organization (O)")
@click.option("--country", default=None, help="Country (C, 2-letter code)")
@click.option(
    "--keys-dir", default=_DEFAULT_KEYS_DIR,
    type=click.Path(), help="Key directory",
)
def ssl_create_csr(
    name: str,
    password_file: str,
    cn: str,
    org: Optional[str],
    country: Optional[str],
    keys_dir: str,
) -> None:
    """Generate a Certificate Signing Request (CSR).

    Ed25519 keys cannot produce traditional X.509 CSRs that most CAs
    accept, so this command generates a temporary ECDSA P-256 key for
    the CSR when the existing key is Ed25519.  The CSR private key is
    saved alongside the original key.
    """
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec, ed25519 as ed_mod
    from cryptography.x509.oid import NameOID

    try:
        km = KeyManager(keys_dir=keys_dir)
        keys_path = Path(keys_dir)

        # Try to load the existing private key.
        existing_key = km.load_private_key(name, password_file)

        # Ed25519 cannot sign a standard X.509 CSR — fall back to EC P-256.
        if isinstance(existing_key, ed_mod.Ed25519PrivateKey):
            click.echo(
                "  \u26a0 Ed25519 key detected — generating EC P-256 key for CSR"
            )
            csr_key = ec.generate_private_key(ec.SECP256R1())
            # Persist the CSR key (encrypted with same password).
            csr_key_pem = csr_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
            csr_key_enc = PasswordManager.encrypt_key(csr_key_pem, password_file)
            csr_key_path = keys_path / f"{name}-csr-private.key"
            csr_key_path.write_bytes(csr_key_enc)
            os.chmod(csr_key_path, 0o600)
            hash_algo: hashes.HashAlgorithm | None = hashes.SHA256()
        else:
            csr_key = existing_key
            hash_algo = hashes.SHA256()

        # Build subject name attributes.
        name_attrs = [x509.NameAttribute(NameOID.COMMON_NAME, cn)]
        if org:
            name_attrs.append(x509.NameAttribute(NameOID.ORGANIZATION_NAME, org))
        if country:
            name_attrs.append(x509.NameAttribute(NameOID.COUNTRY_NAME, country))

        builder = x509.CertificateSigningRequestBuilder().subject_name(
            x509.Name(name_attrs)
        )
        csr = builder.sign(csr_key, hash_algo)

        csr_path = keys_path / f"{name}.csr"
        csr_path.write_bytes(csr.public_bytes(serialization.Encoding.PEM))
        os.chmod(csr_path, 0o644)

        metadata = {
            "name": name,
            "csr_path": str(csr_path),
            "common_name": cn,
            "organization": org,
            "country": country,
            "algorithm": "EC-P256" if isinstance(existing_key, ed_mod.Ed25519PrivateKey) else type(existing_key).__name__,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        click.secho("\u2713 CSR created", fg="green")
        click.echo(json.dumps(metadata, indent=2))

    except Exception as exc:
        click.secho(f"\u2717 Error: {exc}", fg="red", err=True)
        raise SystemExit(1)


@ssl.command("list")
@click.option(
    "--keys-dir", default=_DEFAULT_KEYS_DIR,
    type=click.Path(), help="Key directory",
)
def ssl_list(keys_dir: str) -> None:
    """List all managed keys and their metadata."""
    try:
        km = KeyManager(keys_dir=keys_dir)
        keys = km.list_keys()

        if not keys:
            click.echo("No keys found.")
            return

        for key_name, meta in keys.items():
            click.echo(f"  {key_name}")
            click.echo(f"    Type     : {meta.get('type')}")
            click.echo(f"    Algorithm: {meta.get('algorithm')}")
            click.echo(f"    Key ID   : {meta.get('key_id')}")
            click.echo(f"    Created  : {meta.get('created_at')}")
            if meta.get("parent_ca"):
                click.echo(f"    Parent CA: {meta['parent_ca']}")
            click.echo()

    except Exception as exc:
        click.secho(f"\u2717 Error: {exc}", fg="red", err=True)
        raise SystemExit(1)


@ssl.command("verify")
@click.option("--name", required=True, help="Key name to verify")
@click.option(
    "--keys-dir", default=_DEFAULT_KEYS_DIR,
    type=click.Path(), help="Key directory",
)
def ssl_verify(name: str, keys_dir: str) -> None:
    """Verify key integrity and file permissions."""
    try:
        km = KeyManager(keys_dir=keys_dir)
        valid, message = km.verify_key_integrity(name)
        if valid:
            click.secho(f"\u2713 {message}", fg="green")
        else:
            click.secho(f"\u2717 {message}", fg="red")
            raise SystemExit(1)
    except Exception as exc:
        click.secho(f"\u2717 Error: {exc}", fg="red", err=True)
        raise SystemExit(1)


@ssl.command("rotate")
@click.option("--name", required=True, help="Key name to rotate")
@click.option(
    "--pass", "password_file", required=True,
    type=click.Path(exists=True),
    help="Password file",
)
@click.option(
    "--keys-dir", default=_DEFAULT_KEYS_DIR,
    type=click.Path(), help="Key directory",
)
def ssl_rotate(name: str, password_file: str, keys_dir: str) -> None:
    """Rotate a key (create new version, back up old)."""
    try:
        km = KeyManager(keys_dir=keys_dir)
        metadata = km.rotate_key(name, password_file)
        click.secho("\u2713 Key rotated", fg="green")
        click.echo(json.dumps(metadata, indent=2))
    except Exception as exc:
        click.secho(f"\u2717 Error: {exc}", fg="red", err=True)
        raise SystemExit(1)


# ===================================================================
# Vault command group
# ===================================================================


@click.group("vault")
def vault() -> None:
    """Encrypted secret vault management."""


@vault.command("store")
@click.option("--name", required=True, help="Secret name")
@click.option(
    "--file", "file_path", required=True,
    type=click.Path(exists=True),
    help="File whose content will be stored as the secret",
)
@click.option(
    "--master-pass", "master_pass_file", required=True,
    type=click.Path(exists=True),
    help="Path to master password file",
)
@click.option("--overwrite", is_flag=True, help="Overwrite existing secret")
def vault_store(
    name: str,
    file_path: str,
    master_pass_file: str,
    overwrite: bool,
) -> None:
    """Encrypt and store a secret in the vault."""
    try:
        content = Path(file_path).read_text().strip()
        v = Vault()
        dest = v.store(name, content, master_pass_file, overwrite=overwrite)
        click.secho(f"\u2713 Secret '{name}' stored \u2192 {dest}", fg="green")
    except Exception as exc:
        click.secho(f"\u2717 Error: {exc}", fg="red", err=True)
        raise SystemExit(1)


@vault.command("get")
@click.option("--name", required=True, help="Secret name")
@click.option(
    "--master-pass", "master_pass_file", required=True,
    type=click.Path(exists=True),
    help="Path to master password file",
)
def vault_get(name: str, master_pass_file: str) -> None:
    """Decrypt and print a secret from the vault."""
    try:
        v = Vault()
        secret = v.retrieve(name, master_pass_file)
        click.echo(secret)
    except Exception as exc:
        click.secho(f"\u2717 Error: {exc}", fg="red", err=True)
        raise SystemExit(1)


@vault.command("list")
def vault_list() -> None:
    """List all secrets in the vault."""
    try:
        v = Vault()
        names = v.list_secrets()
        if not names:
            click.echo("Vault is empty.")
            return
        click.echo("Secrets in vault:")
        for n in names:
            click.echo(f"  \u2022 {n}")
    except Exception as exc:
        click.secho(f"\u2717 Error: {exc}", fg="red", err=True)
        raise SystemExit(1)


@vault.command("delete")
@click.option("--name", required=True, help="Secret name to delete")
def vault_delete(name: str) -> None:
    """Remove a secret from the vault."""
    try:
        v = Vault()
        if v.delete(name):
            click.secho(f"\u2713 Secret '{name}' deleted.", fg="green")
        else:
            click.secho(f"Secret '{name}' not found.", fg="yellow")
    except Exception as exc:
        click.secho(f"\u2717 Error: {exc}", fg="red", err=True)
        raise SystemExit(1)


# ===================================================================
# Top-level CLI (groups ssl + vault together)
# ===================================================================


@click.group()
def cli() -> None:
    """dystopian-crypto — Ed25519 key management & secret vault."""


cli.add_command(ssl)
cli.add_command(vault)


if __name__ == "__main__":
    cli()
