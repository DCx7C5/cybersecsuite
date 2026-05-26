"""Accounts API endpoints — CRUD for users, profiles, org management (Phase 7).

Endpoints:
- POST   /api/accounts/register           — Create new account
- GET    /api/accounts/{id}               — Get account details
- GET    /api/accounts/{id}/profile       — Get user profile
- PUT    /api/accounts/{id}/profile       — Update user profile
- POST   /api/organizations               — Create organization
- GET    /api/organizations/{org_id}      — Get org details
- POST   /api/organizations/{org_id}/members  — Add member to org
- GET    /api/organizations/{org_id}/members  — List org members
"""

import msgspec
from css.core.types.base_endpoint import EndpointModel
from css.core.logger import getLogger

from fastapi import APIRouter, HTTPException, status

from css.core.db.models.accounts import (
    Account,
    Organization,
    OrganizationMembership,
    UserProfile,
)

log = getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Request/Response Models
# ─────────────────────────────────────────────────────────────────────────────

class AccountResponse(EndpointModel, kw_only=True):
    """Account response model."""
    id: int
    username: str
    email: str
    is_active: bool
    is_verified: bool
    created_at: str
    last_login: str | None = None


class UserProfileResponse(EndpointModel, kw_only=True):
    """User profile response model."""
    bio: str
    timezone: str
    preferences: dict
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    phone: str | None = None


class RegisterRequest(EndpointModel, kw_only=True):
    """Account registration request."""
    username: str
    email: str
    password: str


class UpdateProfileRequest(EndpointModel, kw_only=True):
    """Update user profile request."""
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    phone: str | None = None
    timezone: str | None = None
    preferences: dict | None = None


class OrganizationResponse(EndpointModel, kw_only=True):
    """Organization response model."""
    id: int
    name: str
    slug: str
    description: str
    tier: str
    is_active: bool
    created_at: str


class CreateOrganizationRequest(EndpointModel, kw_only=True):
    """Create organization request."""
    name: str
    slug: str
    description: str | None = None
    tier: str = "free"


class MembershipResponse(EndpointModel, kw_only=True):
    """Organization membership response."""
    account_id: int
    role: str
    joined_at: str


class AddMemberRequest(EndpointModel, kw_only=True):
    """Add member to organization request."""
    account_id: int
    role: str = "member"


# ─────────────────────────────────────────────────────────────────────────────
# Router
# ─────────────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


# ─────────────────────────────────────────────────────────────────────────────
# Account Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/register", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def register_account(req: RegisterRequest) -> AccountResponse:
    """Register new user account.
    
    Args:
        req: RegisterRequest with username, email, password
        
    Returns:
        AccountResponse with new account details
        
    Raises:
        HTTPException: If username/email already exists or validation fails
    """
    try:
        # Check for existing account
        existing = await Account.get_or_none(username=req.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )
        
        existing = await Account.get_or_none(email=req.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        # Hash password (TODO: use PasswordManager from core.auth)
        from css.core.auth import PasswordManager
        password_hash = PasswordManager.hash_password(req.password)
        
        # Create account
        account = await Account.create(
            username=req.username,
            email=req.email,
            password_hash=password_hash,
        )
        
        # Create empty profile
        await UserProfile.create(account_id=account.id)
        
        log.info(f"Registered new account: {req.username}")
        
        return AccountResponse(
            id=account.id,
            username=account.username,
            email=account.email,
            is_active=account.is_active,
            is_verified=account.is_verified,
            created_at=account.created_at.isoformat(),
        )
    
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Account registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(account_id: int) -> AccountResponse:
    """Get account details.
    
    Args:
        account_id: Account ID
        
    Returns:
        AccountResponse with account details
        
    Raises:
        HTTPException: If account not found
    """
    try:
        account = await Account.get_or_none(id=account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        return AccountResponse(
            id=account.id,
            username=account.username,
            email=account.email,
            is_active=account.is_active,
            is_verified=account.is_verified,
            last_login=account.last_login.isoformat() if account.last_login else None,
            created_at=account.created_at.isoformat(),
        )
    
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Error retrieving account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve account"
        )


@router.get("/{account_id}/profile", response_model=UserProfileResponse)
async def get_user_profile(account_id: int) -> UserProfileResponse:
    """Get user profile.
    
    Args:
        account_id: Account ID
        
    Returns:
        UserProfileResponse with profile details
        
    Raises:
        HTTPException: If account or profile not found
    """
    try:
        profile = await UserProfile.get_or_none(account_id=account_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        return UserProfileResponse(
            first_name=profile.first_name,
            last_name=profile.last_name,
            display_name=profile.display_name,
            avatar_url=profile.avatar_url,
            bio=profile.bio,
            phone=profile.phone,
            timezone=profile.timezone,
            preferences=profile.preferences,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Error retrieving profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile"
        )


@router.put("/{account_id}/profile", response_model=UserProfileResponse)
async def update_user_profile(
    account_id: int,
    req: UpdateProfileRequest,
) -> UserProfileResponse:
    """Update user profile.
    
    Args:
        account_id: Account ID
        req: UpdateProfileRequest with profile fields
        
    Returns:
        Updated UserProfileResponse
        
    Raises:
        HTTPException: If account or profile not found
    """
    try:
        profile = await UserProfile.get_or_none(account_id=account_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Update fields
        if req.first_name is not None:
            profile.first_name = req.first_name
        if req.last_name is not None:
            profile.last_name = req.last_name
        if req.display_name is not None:
            profile.display_name = req.display_name
        if req.avatar_url is not None:
            profile.avatar_url = req.avatar_url
        if req.bio is not None:
            profile.bio = req.bio
        if req.phone is not None:
            profile.phone = req.phone
        if req.timezone is not None:
            profile.timezone = req.timezone
        if req.preferences is not None:
            profile.preferences = {**profile.preferences, **req.preferences}
        
        await profile.save()
        
        return UserProfileResponse(
            first_name=profile.first_name,
            last_name=profile.last_name,
            display_name=profile.display_name,
            avatar_url=profile.avatar_url,
            bio=profile.bio,
            phone=profile.phone,
            timezone=profile.timezone,
            preferences=profile.preferences,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Error updating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Organization Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/organizations", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(req: CreateOrganizationRequest) -> OrganizationResponse:
    """Create new organization.
    
    Args:
        req: CreateOrganizationRequest with org details
        
    Returns:
        OrganizationResponse with new organization
        
    Raises:
        HTTPException: If slug already exists
    """
    try:
        # Check for existing org
        existing = await Organization.get_or_none(slug=req.slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Organization slug already exists"
            )
        
        # Create org
        org = await Organization.create(
            name=req.name,
            slug=req.slug,
            description=req.description or "",
            tier=req.tier or "free",
        )
        
        log.info(f"Created organization: {req.slug}")
        
        return OrganizationResponse(
            id=org.id,
            name=org.name,
            slug=org.slug,
            description=org.description,
            tier=org.tier,
            is_active=org.is_active,
            created_at=org.created_at.isoformat(),
        )
    
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Error creating organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create organization"
        )


@router.get("/organizations/{org_id}", response_model=OrganizationResponse)
async def get_organization(org_id: int) -> OrganizationResponse:
    """Get organization details.
    
    Args:
        org_id: Organization ID
        
    Returns:
        OrganizationResponse with org details
        
    Raises:
        HTTPException: If org not found
    """
    try:
        org = await Organization.get_or_none(id=org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        return OrganizationResponse(
            id=org.id,
            name=org.name,
            slug=org.slug,
            description=org.description,
            tier=org.tier,
            is_active=org.is_active,
            created_at=org.created_at.isoformat(),
        )
    
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Error retrieving organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve organization"
        )


@router.post("/organizations/{org_id}/members", response_model=MembershipResponse, status_code=status.HTTP_201_CREATED)
async def add_organization_member(
    org_id: int,
    req: AddMemberRequest,
) -> MembershipResponse:
    """Add member to organization.
    
    Args:
        org_id: Organization ID
        req: AddMemberRequest with account and role
        
    Returns:
        MembershipResponse with membership details
        
    Raises:
        HTTPException: If org/account not found or already member
    """
    try:
        # Verify org exists
        org = await Organization.get_or_none(id=org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Verify account exists
        account = await Account.get_or_none(id=req.account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        # Check for existing membership
        existing = await OrganizationMembership.get_or_none(
            organization_id=org_id,
            account_id=req.account_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already a member of this organization"
            )
        
        # Create membership
        membership = await OrganizationMembership.create(
            organization_id=org_id,
            account_id=req.account_id,
            role=req.role,
        )
        
        log.info(f"Added {account.username} to org {org.slug}")
        
        return MembershipResponse(
            account_id=membership.account_id,
            role=membership.role,
            joined_at=membership.joined_at.isoformat(),
        )
    
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Error adding organization member: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add member"
        )


@router.get("/organizations/{org_id}/members")
async def list_organization_members(org_id: int) -> list[MembershipResponse]:
    """List organization members.
    
    Args:
        org_id: Organization ID
        
    Returns:
        List of MembershipResponse
        
    Raises:
        HTTPException: If org not found
    """
    try:
        # Verify org exists
        org = await Organization.get_or_none(id=org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Get memberships
        memberships = await OrganizationMembership.filter(organization_id=org_id)
        
        return [
            MembershipResponse(
                account_id=m.account_id,
                role=m.role,
                joined_at=m.joined_at.isoformat(),
            )
            for m in memberships
        ]
    
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Error listing organization members: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list members"
        )


__all__ = ["router"]
