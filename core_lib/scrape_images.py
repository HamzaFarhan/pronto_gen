from tqdm import tqdm
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin, urlparse
from PIL import Image

from core_lib.pronto_conf import *
from core_lib.platform_utils import *
from core_lib.video_utils import verify_image
import requests
import os
import traceback

def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)



def color_to_hex(t):
    #print(t)
    c1 = '#{:02x}'.format(t[0])
    c2 = '{:02x}'.format(t[1])
    c3 = '{:02x}'.format(t[2])
    return c1+c2+c3

def convert_png_to_jpeg(f):
    if os.path.isdir(f):
        print(f'{f} is a directory')
        return 
    with Image.open(f) as im:
        if im.format.lower() != 'png':
            print(f'file {f} is not png returning')
            return None
        c = max(im.getcolors(im.size[0]*im.size[1]))[1]
        #print(c)
        if type(c) == int:
            if c == 0:
                c = 7
            c = list(str(c))
            c[0] = int(c[0])
            c.append(c[0])
            c.append(c[0])
            out = c
            #print('#####')
            print(out)
            #print('#####')
        else:
            #print('CCCC')
            #print(c)
            t = list(c)
            out = []
            for x in t:
                if x < 1.0:
                    x = int(x*255)
                else:
                    x = int(x)
                out.append(x)
            #print('*******')
            print(out)
            #print('********')
            if len(out) == 2:
                out.append(out[1])
            elif len(out) == 1:
                out.append(out[0])
                out.append(out[0])
        fill_color = color_to_hex(out)
        if fill_color == '#000000':
            print('background is black..converting to white')
            fill_color = '#FFFFFF'
            background = Image.new(im.mode[:-1], im.size, fill_color)
            background.paste(im, im.split()[-1])
            im = background

        rgb_im = im.convert('RGB')
        out = f[:f.rfind('.')]
        out = out + '.jpg'
        print(f'out = {out}')
        rgb_im.save(out)
        return out

def convert_to_jpeg(folder,local_root,logger=None):
    supported = ['jpeg','jpg','png','gif']
    if folder[-1] == '/':
        folder = folder[:-1]
        
    local_path = local_root+folder
    files = os.listdir(local_path)
    img_list = []
    for f in files:
        if 'scraped' not in f:
            continue
        ext = f[f.rfind('.')+1:]
        if f[f.rfind('.')+1:] not in supported:
            print('continuing for {}'.format(f))
            continue
        filename = local_path+'/'+f
        out_file_path = filename
        logger.debug(f'out_file_path = {out_file_path}')
        if out_file_path is not None:
            out_file = out_file_path[out_file_path.rfind('/')+1:]
        img_list.append(out_file)
    logger.debug('convert_to_jpeg returning img list')
    logger.debug(img_list)
    return list(set(img_list))
        
def upload_files_to_cloud(files,bucket,folder,local_root=GUEST_VIDEO_BASE,logger=None):
    if folder[-1] != '/':
        folder = folder+'/'
        
    for f in files:
        try:
             local_file = local_root+folder+f
             remote_file = folder+f
             logger.debug(f'uploading file {local_file} to {remote_file}')
             upload_file(bucket,None,local_file,dest_file=remote_file)
        except Exception as e:
            logger.error(f'error uploading file {local_file} to {remote_file}: {e}')
            logger.error(traceback.format_exc())
            
        
        
def download_image(url,folder,local_root='/tmp/guest/',bucket=None,logger=None):
    fname = url.split("/")[-1]
    ext = fname[fname.rfind('.'):]
    fname = fname[:fname.rfind('.')]
    fname += '_scraped'
    fname += ext
    file_with_folder = os.path.join(folder,fname)
    filepath = local_root+file_with_folder
    if os.path.isfile(filepath):
        logger.debug(f'file {filepath} already exists')
        return fname
    # download the body of response by chunk, not immediately
    response = requests.get(url, stream=True)
    # get the total file size
    file_size = int(response.headers.get("Content-Length", 0))
    progress = tqdm(response.iter_content(1024), f"Downloading {fname}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
    with open(filepath, "wb") as f:
        for data in progress:
            f.write(data)
            progress.update(len(data))
    try:  
       #im = rgb_read(filepath)
       im = verify_image(filepath)
    except Exception as e:
        logger.error(f'RGB READ FAILED FOR FILE {filepath} with error {e}--deleting and ignoring file')
        os.remove(filepath)
        return None
            
    return fname



def get_all_images(url):
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko; Google Web Preview) Chrome/41.0.2272.118 Safari/537.36",
               "Referer":"https://www.google.com"}
    soup = bs(requests.get(url,headers=headers).content, "html.parser")
    urls = []
    for img in tqdm(soup.find_all("img"), "Extracting images"):
        img_url = img.attrs.get("src")
        if not img_url:
            img_url = img.attrs.get("data-src")
        if not img_url:
            # if img does not contain src attribute, just skip
            continue
        img_url = urljoin(url, img_url)
        try:
            pos = img_url.index("?")
            img_url = img_url[:pos]
        except ValueError:
            pass
        # finally, if the url is valid
        if is_valid(img_url):
            urls.append(img_url)
    return urls

def scrape_images(url,folder,root_path='/tmp/',bucket=None,logger=None):
    supported = ['jpeg','jpg','png','gif']
    # get all images
    imgs = get_all_images(url)
    print(imgs)
    selected = []
    for img in imgs:
        ext = img[img.rfind('.')+1:]
        if ext not in supported:
            print('continuing for {}'.format(img))
            continue
        # for each image, download it
        img_name = download_image(img,folder,local_root=root_path,bucket=bucket,logger=logger)
        if img_name is not None:
            selected.append(img_name)
    return selected

def scrape_and_save_images(url,bucket,folder,local_root=GUEST_VIDEO_BASE,logger=None):
    create_local_folder(local_root,folder)
    images = scrape_images(url,folder,root_path=local_root,bucket=bucket,logger=logger)
    images = convert_to_jpeg(folder,local_root=local_root,logger=logger)
    upload_files_to_cloud(images,bucket,folder,local_root=GUEST_VIDEO_BASE,logger=logger)
    return images
