# utils/permissions.py
import discord
from config import Config
import logging

logger = logging.getLogger(__name__)


def has_admin_role(member: discord.Member) -> bool:
    """
    Vérifie si un membre a le rôle admin configuré

    Args:
        member: Le membre Discord à vérifier

    Returns:
        bool: True si le membre a le rôle admin ou est administrateur du serveur
    """
    # Vérifier d'abord si c'est un admin du serveur (sécurité de base)
    if member.guild_permissions.administrator:
        logger.info(
            f"Utilisateur {member.name} autorisé en tant qu'administrateur du serveur"
        )
        return True

    # Vérifier le rôle spécifique
    admin_role = discord.utils.get(member.roles, name=Config.ADMIN_ROLE_NAME)

    if admin_role:
        logger.info(
            f"Utilisateur {member.name} autorisé avec le rôle {Config.ADMIN_ROLE_NAME}"
        )
        return True

    logger.warning(
        f"Utilisateur {member.name} non autorisé - rôle {Config.ADMIN_ROLE_NAME} requis"
    )
    return False


def get_permission_error_message() -> str:
    """
    Retourne le message d'erreur de permission personnalisé

    Returns:
        str: Message d'erreur formaté
    """
    return f"❌ Permission refusée - Rôle `{Config.ADMIN_ROLE_NAME}` ou Administrateur requis"


async def send_permission_denied(channel: discord.TextChannel,
                                 delete_after: int = 5) -> discord.Message:
    """
    Envoie un message de permission refusée qui s'auto-supprime

    Args:
        channel: Le canal où envoyer le message
        delete_after: Délai avant suppression automatique

    Returns:
        discord.Message: Le message envoyé
    """
    return await channel.send(get_permission_error_message(),
                              delete_after=delete_after)


def has_role_by_name(member: discord.Member, role_name: str) -> bool:
    """
    Vérifie si un membre a un rôle spécifique par son nom

    Args:
        member: Le membre Discord à vérifier
        role_name: Le nom du rôle à chercher

    Returns:
        bool: True si le membre a ce rôle
    """
    role = discord.utils.get(member.roles, name=role_name)
    return role is not None


def get_user_roles(member: discord.Member) -> list:
    """
    Retourne la liste des noms de rôles d'un utilisateur (excluant @everyone)

    Args:
        member: Le membre Discord

    Returns:
        list: Liste des noms de rôles
    """
    return [role.name for role in member.roles if role.name != "@everyone"]


def check_role_exists(guild: discord.Guild, role_name: str) -> bool:
    """
    Vérifie si un rôle existe sur le serveur

    Args:
        guild: Le serveur Discord
        role_name: Le nom du rôle à chercher

    Returns:
        bool: True si le rôle existe
    """
    role = discord.utils.get(guild.roles, name=role_name)
    return role is not None
