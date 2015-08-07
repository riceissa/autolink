#!/usr/bin/python3
# -*- coding: utf-8 -*-

from jinja2 import Template, Environment, FileSystemLoader

TEST_CASES = [
    # (og_title, title, meta_title, h1)
    ("The Biodeterminist&#39;s Guide to Parenting", "Issa Rice | Issa Rice", None, "Issa Rice"),
    (None, "Issa Rice | Issa Rice", None, "Issa Rice"),
    (None, "Issa Rice | Issa Rice", "The Biodeterminist&#39;s Guide to Parenting", "Issa Rice"),
    (None, "Experiences in applying &quot;The Biodeterminist's Guide to Parenting&quot; - Less Wrong Discussion", None, "Issa Rice"),
    (None, "Jackdaws love my big sphinx of quartz - The Biodeterminist's Guide to Parenting", None, "Issa Rice"),
    (None, "Jackdaws love my big sphinx of quartz - The Biodeterminist's Guide to Parenting - and one more", None, "Issa Rice"),
    (None, "Beautiful Soup: We called him Tortoise because he taught us.", None, "Issa Rice"),
    (None, "CP Wiki: Beautiful Soup: We called him Tortoise because he taught us.", None, "Issa Rice"),
    (None, "CP Wiki: Beautiful Soup: We called him Tortoise because he taught us - Less Wrong", None, "Issa Rice"),
    (None, "Themes and Theming &mdash; The Dojo Toolkit - Reference Guide", None, "Issa Rice"),
    (None, "Themes and Theming — The Dojo Toolkit - Reference Guide", None, "Issa Rice"),
    (None, "Themes and Theming - The Dojo Toolkit - Reference Guide", None, "Issa Rice"),
    (None, "Code of Federal Regulations | HHS.gov", None, "Issa Rice"),
    (None, "Jackdaws love my big sphinx of quartz - The Biodeterminist's Guide to Parenting - and one more", None, "Issa Rice"),
    (None, "Jackdaws love my big sphinx of quartz - The Biodeterminist's Guide to Parenting - and one more", None, "Issa Rice"),
]

def main():
    env = Environment(loader=FileSystemLoader("."))
    skeleton = env.get_template("template.html")
    for n, v in enumerate(TEST_CASES):
        filename = "test_html/test{}.html".format(n)
        final = skeleton.render(
            og_title=v[0],
            title=v[1],
            meta_title=v[2],
            h1=v[3]
        )
        with open(filename, "w") as f:
            f.write(final)

if __name__ == "__main__":
    main()
