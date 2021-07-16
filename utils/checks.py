async def is_mod(ctx):
    for role in ctx.author.roles:
        if role.id in ctx.bot.config["modRoleIDs"]:
            return True

    return False


def is_owner(ctx):
    return ctx.author.id in ctx.bot.config["ownerIDs"]
