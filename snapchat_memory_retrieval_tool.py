import json
import pathlib
import asyncio
import aiohttp
import aiofiles
import timeit
import datetime

# For download statistic checking
total_num_downloads = 0
successful_posts, failed_posts = 0, 0
successful_downloads, failed_downloads = 0, 0

# For keeping files and dates paired correctly
processed_urls = {"url": [], "path": []}

# For use in file path formatting
months = {'01': 'Jan', '02': 'Feb', '03': 'Mar',
          '04': 'Apr', '05': 'May', '06': 'Jun',
          '07': 'Jul', '08': 'Aug', '09': 'Sep',
          '10': 'Oct', '11': 'Nov', '12': 'Dec'}
types = {'PHOTO': 'Photos', 'VIDEO': 'Videos'}


def get_formatted_urls():
    """
    Get properly formatted urls and dates from the memories json.

    The urls gotten here will later be used for POST requests.
    The dates gotten here will later be used for file pathing.
    Each url and its date are returned as a key-pair in a dict,
    which is done to ensure they stay together throughout the process.
    """
    global total_num_downloads

    json_location = "./memories_history.json"  # Default is current directory

    with open(json_location, "r") as memories_json:
        memories = json.load(memories_json)

    json_urls = []
    paths = []
    # The range in this for loop controls how many memories are downloaded
    for memory in range(len(memories["Saved Media"])): 
        json_urls.append(memories["Saved Media"][memory]["Download Link"])
        year = (memories["Saved Media"][memory]["Date"]).split('-')[0]
        month = months[(memories["Saved Media"][memory]["Date"]).split('-')[1]]
        media_type = types[(memories["Saved Media"][memory]["Media Type"])]
        path = 'media/{0}/{1}/{2}'.format(year, month, media_type)
        paths.append(path)

    total_num_downloads = len(json_urls)

    return dict(zip(json_urls, paths))


async def get_s3_url(session, formatted_url, formatted_urls):
    """
    Get AWS S3 download link from a link in the memories json.

    Each url from the memories json needs to be used to make POST requests.
    The response from these requests will be a AWS S3 bucket item link. 
    The link is then added to a dictionary that will contain both 
    the download link, and the path (which was gotten from the memory's date).
    """
    global successful_posts
    global failed_posts

    async with session.post(formatted_url) as response:
        text_response = await response.text()
        if response.status == 200:
            processed_urls['url'].append(text_response)
            processed_urls['path'].append(formatted_urls[formatted_url])
            successful_posts += 1
        else:
            failed_posts += 1


async def download_file(session, processed_url, dir):
    """
    Download a file, given a valid download link, and a path to download it to.
    The dictionary containing each AWS S3 bucket item link and corresponding
    is used to download each memory and store it relative to the date the
    memory was originally created/saved.
    """
    global total_num_downloads
    global successful_downloads
    global failed_downloads

    success = False

    async with session.get(processed_url) as resp:
        if resp.status == 200:
            success = True
            filename = processed_url.split('/')[5].split('?')[0]
            path = '{}/{}'.format(dir, filename)
            pathlib.Path(dir).mkdir(parents=True, exist_ok=True)
            f = await aiofiles.open(path, mode='wb')
            await f.write(await resp.read())
            await f.close()

    if(success):
        successful_downloads += 1
        print("--> Downloaded memory {} out of {}"
              .format(successful_downloads, total_num_downloads))
    else:
        failed_downloads += 1


async def retrieve_memories():
    """Puts everything together and retrieves the snapchat memories

    The order of operations will go as follows:
    1. Data from the memories json will be formatted so that it is more usable
    2. A list of download links will be created using this data
    3. Memories will then be downloaded accordignly based off of this list
    """
    try:
        formatted_urls = get_formatted_urls()
    except FileNotFoundError:
        print("\nCannot proceed without json file. Stopping...\n")
        loop = asyncio.get_running_loop()
        loop.stop()
        exit(0)
    except ValueError:
        print("\nBad json file. Stopping...\n")
        loop = asyncio.get_running_loop()
        loop.stop()
        exit(0)

    print('Getting download links...')
    async with aiohttp.ClientSession() as session:
        tasks = [get_s3_url(session, formatted_url, formatted_urls)
                 for formatted_url in formatted_urls]
        await asyncio.gather(*tasks)
    print('DONE!\n')

    print('Downloading memories...')
    async with aiohttp.ClientSession() as session:
        tasks = [download_file(session, processed_urls['url'][memory],
                               processed_urls['path'][memory])
                 for memory in range(len(processed_urls['url']))]
        await asyncio.gather(*tasks)
    print('DONE!\n')


def run():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(retrieve_memories())


if __name__ == '__main__':
    # Run and time the program
    starttime = timeit.default_timer()
    run()
    stoptime = timeit.default_timer() - starttime
    time = str(datetime.timedelta(seconds=stoptime))
    hours = time.split(':')[0]
    minutes = time.split(':')[1]
    seconds = time.split(':')[2]

    # Printing out download statistics
    print("Downloaded {} memories in: ".format(successful_downloads))
    print("{} hours {} minutes {} seconds".format(hours, minutes, seconds))
    print("\n# of POST successes : {}".format(successful_posts))
    print("# of POST failures  : {}".format(failed_posts))
    print("# of download successes : {}".format(successful_downloads))
    print("# of download failures  : {}".format(failed_downloads))

    exit(0)
