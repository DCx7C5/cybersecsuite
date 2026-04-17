"""
CLI Integration documentation for dystopian-crypto tool.
This shows how to integrate the KeyManager with CLI commands.

To be implemented in: https://github.com/DCx7C5/dystopian-crypto
"""

# EXAMPLE CLICK-BASED CLI IMPLEMENTATION

import click
from pathlib import Path
from crypto.key_manager import KeyManager, PasswordManager


@click.group()
def ssl():
    """SSL/RSA Key management for dystopian infrastructure."""
    pass


@ssl.command()
@click.option(
    "--name", required=True, help="CA name (e.g., RootCA, IntermediateCA)"
)
@click.option(
    "--password-file",
    required=True,
    type=click.Path(exists=True),
    help="Path to file containing CA password",
)
@click.option(
    "--key-size",
    default=2048,
    type=click.Choice(["2048", "3072", "4096"]),
    help="RSA key size",
)
@click.option(
    "--output-dir",
    default="/etc/dystopian-crypto/keys",
    type=click.Path(),
    help="Output directory for keys",
)
@click.option("--overwrite", is_flag=True, help="Overwrite existing keys")
def createca(name: str, password_file: str, key_size: str, output_dir: str, overwrite: bool):
    """
    Create a Certificate Authority with password-protected RSA keys.

    USAGE:
        dystopian-crypto ssl createca --name RootCA --password-file /root/.ca-pass

    The password file should contain the CA password (one line, no newline).
    For maximum security:
    - Create password file: echo "your_secure_password" > /root/.ca-pass
    - Restrict permissions: chmod 600 /root/.ca-pass
    - Store password file securely (ideally in hardware token or vault)
    """
    try:
        km = KeyManager(keys_dir=output_dir)

        click.echo(f"Creating CA: {name}")
        click.echo(f"  Key size: {key_size} bits")
        click.echo(f"  Output dir: {output_dir}")
        click.echo()

        metadata = km.create_ca_keypair(
            name=name,
            password_file=password_file,
            key_size=int(key_size),
            overwrite=overwrite,
        )

        click.secho("✓ CA created successfully", fg="green")
        click.echo()
        click.echo("Metadata:")
        click.echo(f"  Key ID: {metadata['key_id']}")
        click.echo(f"  Created: {metadata['created_at']}")
        click.echo(f"  Private key: {metadata['private_key_path']}")
        click.echo(f"  Public key: {metadata['public_key_path']}")
        click.echo()
        click.echo("Next steps:")
        click.echo(f"  1. Use key_id '{metadata['key_id']}' in configurations")
        click.echo(f"  2. Store password file securely: {password_file}")
        click.echo(f"  3. Create signing keys: dystopian-crypto ssl createsigning ...")

    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")
        raise SystemExit(1)


@ssl.command()
@click.option("--name", required=True, help="Signing key name")
@click.option("--ca-name", required=True, help="Parent CA name")
@click.option(
    "--password-file",
    required=True,
    type=click.Path(exists=True),
    help="Password file",
)
@click.option(
    "--key-size",
    default=2048,
    type=click.Choice(["2048", "3072", "4096"]),
)
@click.option(
    "--output-dir",
    default="/etc/dystopian-crypto/keys",
    type=click.Path(),
)
def createsigning(
    name: str, ca_name: str, password_file: str, key_size: str, output_dir: str
):
    """
    Create a signing key under a CA.

    USAGE:
        dystopian-crypto ssl createsigning --name artifact-signer \
          --ca-name RootCA --password-file /root/.ca-pass
    """
    try:
        km = KeyManager(keys_dir=output_dir)

        click.echo(f"Creating signing key: {name}")
        click.echo(f"  Parent CA: {ca_name}")

        metadata = km.create_signing_keypair(
            name=name,
            ca_name=ca_name,
            password_file=password_file,
            key_size=int(key_size),
        )

        click.secho("✓ Signing key created", fg="green")
        click.echo(f"  Key ID: {metadata['key_id']}")

    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")
        raise SystemExit(1)


@ssl.command()
@click.option("--output-dir", default="/etc/dystopian-crypto/keys")
def listkeys(output_dir: str):
    """List all managed keys with metadata."""
    try:
        km = KeyManager(keys_dir=output_dir)
        keys = km.list_keys()

        if not keys:
            click.echo("No keys found")
            return

        click.echo("Available keys:")
        click.echo()

        for key_name, metadata in keys.items():
            click.echo(f"  {key_name}")
            click.echo(f"    Type: {metadata.get('type')}")
            click.echo(f"    Key ID: {metadata.get('key_id')}")
            click.echo(f"    Key size: {metadata.get('key_size')} bits")
            click.echo(f"    Created: {metadata.get('created_at')}")
            if metadata.get("parent_ca"):
                click.echo(f"    Parent CA: {metadata.get('parent_ca')}")
            click.echo()

    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")
        raise SystemExit(1)


@ssl.command()
@click.option("--name", required=True, help="Key name to verify")
@click.option("--output-dir", default="/etc/dystopian-crypto/keys")
def verify(name: str, output_dir: str):
    """Verify key integrity and permissions."""
    try:
        km = KeyManager(keys_dir=output_dir)
        valid, message = km.verify_key_integrity(name)

        if valid:
            click.secho(f"✓ {message}", fg="green")
        else:
            click.secho(f"✗ {message}", fg="red")
            raise SystemExit(1)

    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")
        raise SystemExit(1)


@ssl.command()
@click.option("--name", required=True, help="Key name to rotate")
@click.option(
    "--password-file",
    required=True,
    type=click.Path(exists=True),
    help="Password file",
)
@click.option(
    "--new-key-size",
    default=2048,
    type=click.Choice(["2048", "3072", "4096"]),
)
@click.option("--output-dir", default="/etc/dystopian-crypto/keys")
def rotate(
    name: str, password_file: str, new_key_size: str, output_dir: str
):
    """Rotate a key to new version."""
    try:
        km = KeyManager(keys_dir=output_dir)

        click.echo(f"Rotating key: {name}")
        metadata = km.rotate_key(name, password_file, int(new_key_size))

        click.secho("✓ Key rotated", fg="green")
        click.echo(f"  New key ID: {metadata['key_id']}")
        click.echo(f"  Rotated at: {metadata['rotated_at']}")

    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")
        raise SystemExit(1)


if __name__ == "__main__":
    ssl()


# INTEGRATION INSTRUCTIONS FOR dystopian-crypto

"""
1. INSTALL DEPENDENCIES:
   - cryptography>=43.0.0
   - click>=8.1.0

2. ADD TO pyproject.toml [project.scripts]:
   dystopian-crypto = "dystopian_crypto.cli:cli"

3. IMPORT AND REGISTER:
   from src.crypto.key_manager import KeyManager
   
   @click.group()
   def ssl():
       pass
   
   @ssl.command()
   def createca(...): ...
   
   main.add_command(ssl)

4. SECURITY BEST PRACTICES:
   - Password files must be restricted: chmod 600 /path/to/password
   - Store passwords in hardware tokens, vaults, or encrypted filesystems
   - Use separate passwords for each key
   - Rotate keys every 90 days (or per security policy)
   - Audit key access via syslog

5. EXAMPLE WORKFLOW:
   
   # Create password file securely
   $ openssl rand -base64 32 > /root/.ca-password
   $ chmod 600 /root/.ca-password
   
   # Create CA
   $ dystopian-crypto ssl createca --name RootCA \\
     --password-file /root/.ca-password \\
     --key-size 4096
   
   # Create signing key
   $ dystopian-crypto ssl createsigning --name artifact-signer \\
     --ca-name RootCA \\
     --password-file /root/.ca-password
   
   # List keys
   $ dystopian-crypto ssl listkeys
   
   # Verify integrity
   $ dystopian-crypto ssl verify --name RootCA
   
   # Rotate key (create new version)
   $ dystopian-crypto ssl rotate --name artifact-signer \\
     --password-file /root/.ca-password

6. INTEGRATION WITH cybersecsuite:
   
   from crypto.key_manager import KeyManager
   from crypto.ssl_signer import SSLArtifactSigner
   
   # Create KeyManager
   km = KeyManager("/etc/dystopian-crypto/keys")
   
   # Initialize signer with password-protected key
   signer = SSLArtifactSigner(
       key_id="artifact-signer",
       key_manager=km,
       password_file="/root/.ca-password"
   )
   
   # Now all artifact signing is automatic with password protection
"""

