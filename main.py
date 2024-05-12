import asyncio
import os
import re
import discord
import urllib.parse

from discord.ext import commands
from typing import Set
from api import KeepaApiClient, api_key
from seller import Seller, remove_seller_by_id, get_all_sellers_formatted


keepa_api = KeepaApiClient(api_key)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

monitored_sellers: Set[Seller] = set()

monitor_interval = 3600
channel_name = "general"

def format_text(text):
    return f"```{text}```"

def format_product_info(product_info, seller_name, seller_id):
    embed = discord.Embed(title="Product Information", url=f"https://www.amazon.com/dp/{product_info['ASIN']}", description="We have found a new product", color=0x074b6c)
    embed.add_field(name="ASIN", value=product_info['ASIN'], inline=True)
    embed.add_field(name="Seller Name", value=f"[{seller_name}](https://www.amazon.com/sp?seller={seller_id})", inline=True)
    embed.add_field(name="Brand", value=product_info['Brand'], inline=True)
    embed.add_field(name="Category", value=product_info['Category'], inline=True)
    embed.add_field(name="Sales rank", value=str(product_info['Sales rank']), inline=True)
    embed.add_field(name="Buy Box Price", value=f"${round(product_info['Buy Box Price'], 2)}", inline=True)
    embed.add_field(name="Avg. 90-day", value=f"${round(product_info['Avg. 90-day'], 2)}", inline=True)
    embed.add_field(name="Offers", value=product_info['Offers'], inline=True)
    google_link = f"https://www.google.com/search?q={urllib.parse.quote(str(product_info['Google title']))}"
    embed.add_field(name="Google title", value=f"[{product_info['Google title']}]({google_link})", inline=True)
    embed.add_field(name="Google model", value=f"[{product_info['Google model']}](https://www.google.com/search?q={urllib.parse.quote(str(product_info['Google model']))})", inline=True)
    embed.add_field(name="UPC", value=f"[{product_info['UPC']}](https://www.google.com/search?q={urllib.parse.quote(str(product_info['UPC']))})", inline=True)

    pattern = r"(width|height)=\d+"
    new_url = re.sub(pattern, 'width=350', product_info["Image"])
    new_url = re.sub(pattern, 'height=350', new_url)
    embed.set_thumbnail(url=new_url)
    embed.set_image(url="attachment://plot.png")
    return embed


async def montitor_sellers():
    channel = discord.utils.get(bot.get_all_channels(), name=channel_name)
    for seller in monitored_sellers:
        seller_products = None
        try:
            
            seller_products = keepa_api.get_seller_products(seller.id)
            new_items = seller_products.difference(seller.products)

            if len(new_items) <= 0:
                continue
            
            for item in new_items:
                details, _ = keepa_api.get_product_details(item)
                text = format_product_info(details, seller.name, seller.id)
                try:
                    plot = keepa_api.get_product_price_graph(details.get("ASIN"),salesrank=1, bb=1, fba=1, fbm=1)
                    await channel.send(embed=text, file=plot)
                    #if os.path.exists("plot.png"):
                     #   os.remove("plot.png")
                except Exception as e:
                    await channel.send(embed=text)

        except Exception as e:
            print(e)

        finally:
            if seller_products:
                seller.products = seller_products
            
            
    
@bot.command()
async def setChannelName(ctx, message):
    global channel_name
    try:
        channel = discord.utils.get(bot.get_all_channels(), name=message)
        await channel.send(format_text("Amazon bot has entered the chat!"))
        channel_name = message
    except:
        await channel.send(format_text("Error, The channel doesnt look right"))
    
@bot.command()
async def setMonitorDuration(ctx, message):
    global monitor_interval
    try:
        channel = discord.utils.get(bot.get_all_channels(), name=channel_name)
        await channel.send(format_text(f"Set check intervel to {int(message)} successfully."))
        monitor_interval = int(message)
    except:
        await channel.send(format_text("Error, The number doesnt look right"))
        
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    channel = discord.utils.get(bot.get_all_channels(), name=channel_name)
    await channel.send(format_text("Amazon bot has entered the chat!. Type !commands for all the commands :)"))
    while True:
        await montitor_sellers()
        await asyncio.sleep(monitor_interval)
        
@bot.command()
async def commands(ctx):
    channel = discord.utils.get(bot.get_all_channels(), name=channel_name)
    commands = """
    Here is the command list:
        !commands : Displays a list of the commands available.
        !removeSeller : Removes a seller. Takes in a seller ID
        !addSeller : Adds a seller to monitor. Takes in a seller ID
        !getAllSellers : Gets all the sellers being monitored now.
        !getSellerProducts : Gets all the products for a seller.
        !setChannelName: To set the channel name
        !setMonitorDuration: To set monitor duration its 60 minutes by default, The value must be in seconds
    """
    await channel.send(format_text(commands))

@bot.command()
async def removeSeller(ctx, message: str):
    channel = discord.utils.get(bot.get_all_channels(), name=channel_name)
    if message not in monitored_sellers:
        await channel.send(format_text("Seller not found"))
        return 
    
    remove_seller_by_id(message, monitored_sellers)
    formatted_sellers = get_all_sellers_formatted(monitored_sellers)
    await channel.send(format_text(f"""Removed {message} from the monitoring list. Here are all the sellers we are monitoring{formatted_sellers}"""))

@bot.command()
async def getSellerProducts(ctx, message: str):
    channel = discord.utils.get(bot.get_all_channels(), name=channel_name)
    if message not in monitored_sellers:
        await channel.send(format_text("Seller not found"))
        return 
    
    products = keepa_api.get_seller_products(seller_id=message)
    await channel.send(format_text(f"""Here are all the products for {message}, {",".join(products)}"""))

@bot.command()
async def addSeller(ctx, message: str):
    channel = discord.utils.get(bot.get_all_channels(), name=channel_name)
    name = keepa_api.get_seller_name(message)
    if not name:
        channel.send(format_text("Invalid seller id as no name can be derived from the ID"))
        
    products = keepa_api.get_seller_products(message)
    
    monitored_sellers.add(Seller(name=name, id=message, products=products))
    
    formatted_sellers = get_all_sellers_formatted(monitored_sellers)
    await channel.send(format_text(f"""Added {message} to the monitoring list. Their name is {name}. Here are all the sellers we are monitoring{formatted_sellers}"""))

@bot.command()
async def getAllSellers(ctx: str):
    channel = discord.utils.get(bot.get_all_channels(), name=channel_name)
    if formatted_sellers := get_all_sellers_formatted(monitored_sellers):
        await channel.send(format_text(f"""Here are all the sellers we are monitoring{formatted_sellers}"""))
    else:
        await channel.send(format_text("We are not monitoring any sellers currently"))
    

    
if __name__ == "__main__":
    # Discord key you can replace it with your own
    import os
    bot.run(os.getenv("BOT_TOKEN"))
