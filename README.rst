Tickertock
==========

A wrapper for `streamdeck_ui` to link it up to Clockify.

Using a StreamDeck for
this seemed like a waste of money until compared against losing an hour of
consultancy billing, and I dunno about anyone else, but I have saved many
hours through this little jobbie versus trying to be disciplined using the
desktop app or browser plugins.

With many thanks to the StreamDeck and `streamdeck_ui` folks, who
did 99.99% of the work, which I just in imported (aside from the
other open source libs obvs :D).

Installation
------------

"Nothing works, there's no buttons!"

Do you actually have a StreamDeck? Have a look at `Elgato's website <https://www.elgato.com/en/stream-deck>`_
and imagine yourself doing something way less cool with one. This has been tested
with 6- and 15- key decks on Linux.

"Nothing works, there's no setup.py file!"

That's right. I have fought with (and alongside) pipenv, poetry, generations
of pip, conda, setuptools, distutils and others. Now I there is a standard and
I am sticking to it. PEP621 is the hill I shall defend. It may be half-supported, and
have weirdnesses and I spent half an hour trying to get package data to
install (like every other Python packaging experience that I have had), but
it's a PEP, and some day we will live in an Avalon of packaging consistency.
And this package will install.

Make sure that you have a recent pip and setuptools, then:

    pip install .

"Why are there no tests"

Because this spent most of its life as a gluescript and custom changes to
streamdeck_ui, which did not deserve to pass tests. Now I have got frustrated
patching it, and other people want to use this, so this is step 1 of tidying
up. The other steps involve tests, once actual use for this is established.
In the meantime, PR heroes welcome.

Usage
-----

To initialize:

    tickertock init --clockify-api-key APIKEY --clockify-workspace-id WORKSPACEID

Once this is up, you should have a directory `~/.config/tickertock` with a bunch
of config. In particular, a `projects.toml` file with your projects from
Clockify. You can rearrange the order of these (or remove any) from the `entries`
list to change how they get ordered on your StreamDeck.

If you want fancier icons, put 128x128 icons into the `~/.config/tickertock/assets`
folder with lowercase names (PNGs) matching your projects (e.g. General ->
general.png)

You can customize the names, which will change the button text (and expected
asset PNG name, if used) by altering the key in the projects map (e.g. to Accounts)
and updating the matching name in `entries`. For instance:

    [projects.Accounts]
    
    "Accounts System Logs"
    colour = "9C27B0"
    ...
    [page]
    entries = [
    "Accounts",
    ...

This works provided you keep the ``name = "..."`` matching Clockify.

Once it is set up, you can run `tickertock ui`. This is a thin wrapper around
the StreamDeck UI tool and you should get a taskbar icon of theirs appearing.
When you toggle to timetrack, this image will update to your project logo.
In theory, you could try configuring the StreamDeck via their configuration UI,
but I don't know how that'll go for you, as we patch it on load. YMMV.

You can use `tickertock writeout` to get output config if you just want to get
an initial setup that you can customize with the full streamdeck_ui
functionality.

Scripting Clockify is also then as easy as:

    tickertock toggle Accounts

to start the Accounts project tracking, and

    tickertock toggle None

to stop any active tracking.

Functionality
-------------

While this is running on a StreamDeck, the button in the bottom-right corner
is special. All the others should be project icons and pressing them will
start tracking on that project.

If you stop tracking, then the bottom-right indicator should show a big red
icon to warn you. If you are tracking, it should show "@" followed by the name
of the project. As time goes on it shows a clockface to indicate minutes tracked
and, if you go over an hour, a number indicating the hours on the project.

It syncs from Clockify every 30s, so it should automatically show the active
project when started, and if you change something in Clockify or the browser
plugin, you should see it shortly update on your device.

Repeatedly pressing the bottom-right button will cycle through the pages,
showing all your projects. It should correctly rearrange if you plug a bigger
or smaller deck in, but I have not tried with multiple at once (should be
fixable by a PR if it doesn't work, as we always loop through attached decks).

License
-------

MIT License, 2020- Phil Weir.
