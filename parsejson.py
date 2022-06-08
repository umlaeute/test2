#!/usr/bin/env python3

import re
import os


def parseArgs():
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--filename",
        help="alternative filename if DATA does not contain any",
    )

    parser.add_argument(
        "--title",
        help="short description of the tip",
    )
    parser.add_argument(
        "--details",
        action="append",
        help="longer explanation of the tip",
    )
    parser.add_argument(
        "--url",
        help="link to additional information on the topic",
    )
    parser.add_argument(
        "--image",
        help="(animated) GIF file for the tip (can be remote)",
    )

    parser.add_argument("--author", help="submitter of the the tip")

    parser.add_argument(
        "--outdir",
        default=".",
        help="output directory",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="raise verbosity (can be given multiple times",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="count",
        default=0,
        help="lower verbosity (can be given multiple times",
    )

    parser.add_argument(
        "data",
        nargs="?",
        help="JSON formatted dictionary with all the data",
    )

    args = parser.parse_args()
    args.verbose = args.verbose - args.quiet
    del args.quiet
    return args


def getJSONData(s):
    import json

    if not s:
        return {}
    try:
        return json.loads(s)
    except ValueError:
        pass
    return {}


def args2dict(d, args, keys=[]):
    ## get default values for 'keys' from 'args'
    for k in keys:
        try:
            d[k] = d.get(k, getattr(args, k))
            if d[k] is None:
                del d[k]
        except AttributeError:
            pass
    return d


def getData(args):
    d0 = {}
    if args.data:
        d0 = getJSONData(args.data)
    d0 = args2dict(
        d0,
        args,
        ["filename", "title", "details", "url", "image", "author"],
    )
    d0 = {k: v.strip() for k, v in d0.items()}
    data = {}
    # cleanup filename
    data["filename"] = (
        d0.get("filename", "")
        .strip("/")
        .replace("/", "-")
        .replace("\n", "")
        .replace(" ", "")
    )
    # cleanup title
    data["title"] = d0.get("title", "").replace("\n", " ")
    # cleanup details (get rid of code-block)
    details = d0.get("details", "")
    try:
        details = re.split(r"^(.{3})[^\n]*\n(.*)\1", details, flags=re.DOTALL)[2]
    except IndexError:
        pass
    data["details"] = details.splitlines()
    # cleanup image (get rid of markdown)
    try:
        data["image"] = re.split(
            r".*]\((.*\.gif)\)", d0.get("image", "").replace("\n", "")
        )[1]
    except IndexError:
        pass
    # cleanup url
    url = d0.get("url", "").replace("\n", " ")
    if url.startswith("http://") or url.startswith("https://"):
        data["url"] = url
    # cleanup author
    data["author"] = d0.get("author", "").replace("\n", " ")

    return data


def makeTXT(filename, title, details, url="", author="", outdir=".", **kwargs):
    data = []
    filename = os.path.join(outdir, "%s.txt" % filename)
    if title:
        data.append("TITLE\t%s" % title)
    if details:
        data += ["DETAILS\t%s" % _ for _ in details]
    if url:
        data.append("URL\t%s" % url)
    if author:
        data.append("AUTHOR\t%s" % author)

    with open(filename, "w") as f:
        f.write("\n".join(data))
        f.write("\n")


def makeGIF(filename, image="", outdir="", **kwargs):
    import requests

    if not image:
        return
    filename = os.path.join(outdir, "%s.gif" % filename)
    with requests.get(image, stream=True) as r:
        r.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                # if chunk:
                f.write(chunk)


if __name__ == "__main__":
    args = parseArgs()
    d = getData(args)
    d["outdir"] = args.outdir
    if (not d["title"]) or (not d["details"]):
        raise (Exception("'title' and 'details' are required"))
    makeTXT(**d)
    makeGIF(**d)
