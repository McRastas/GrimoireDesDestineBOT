import discord
from discord.ui import Button, View


class SuppressView(View):

    def __init__(self, author):
        super().__init__(timeout=60)
        self.author = author

    @discord.ui.button(label="Supprimer",
                       style=discord.ButtonStyle.danger,
                       emoji="🗑️")
    async def delete_button(self, interaction: discord.Interaction,
                            button: Button):
        if interaction.user == self.author or interaction.user.guild_permissions.manage_messages:
            await interaction.message.delete()
        else:
            await interaction.response.send_message(
                "Vous n'avez pas la permission de supprimer ce message.",
                ephemeral=True)
