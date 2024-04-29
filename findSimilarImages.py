import pickle
from PIL import Image
import imagehash
import os
import time
from math import factorial


def get_image_files(dirname):
    matches = []
    for root, dirnames, filenames in os.walk(dirname):
        for filename in filenames:
            if filename.lower().endswith(('.png', '.jpeg', '.jpg', '.webp')) and not filename.startswith('.'):
                matches.append(os.path.join(root, filename))
    print('found', len(matches), 'image files')
    return matches


def similarity_percentage(hash1, hash2):
    if len(hash1) != len(hash2):
        raise ValueError("Error: hashes must be of equal length")
    similarity = sum(c1 == c2 for c1, c2 in zip(hash1, hash2)) / len(hash1)
    return similarity * 100


def get_phash(dirname, image, hash_size):
    with Image.open(os.path.join(dirname, image)) as img:
        hash = str(imagehash.phash(img, hash_size))
    return (hash)


CACHE_FILE = "phash_cache.pkl"


def load_cache():
    try:
        with open(CACHE_FILE, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}


def save_cache(cache):
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(cache, f)


def find_similar_images(dirname, hash_size, threshold):
    start = time.time()
    image_file_names = get_image_files(dirname)
    if (len(image_file_names) < 2):
        return([])
    hashes = {}
    results = []
    cache = load_cache()  # Load the cache from file

    #  get hash of every image file
    for image in image_file_names:
        try:
            if image not in cache:
                cache[image] = get_phash(dirname, image, hash_size)
            hashes[image] = cache[image]
        except:
            print('error', image)

    print('got phash for', len(hashes), 'image files')

    def combinations(n): return factorial(n) // (2 * factorial(n - 2))

    # compare the hashes
    for i, (img1, hash1) in enumerate(hashes.items()):
        for img2, hash2 in list(hashes.items())[i+1:]:
            similarity = similarity_percentage(hash1, hash2)
            if (similarity > threshold):
                print(str(similarity)+"% -", img1, "&", img2)
                results.append([img1, img2, similarity])

    print(str(len(hashes)) + " files or " + str(combinations(len(hashes)))+" combinations checked in " +
          str(time.time()-start) + " seconds")

    # Save the updated cache
    save_cache(cache)

    return results
