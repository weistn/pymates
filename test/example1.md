\pagesize(A4)
\margin(20*mm, 20*mm, 60*mm, 20*mm)
\pageBox("mybox", (160*mm, 20*mm, 40*mm, 200*mm))

# Hello World

\mybox A B C D E F G H I J K L M N

Here comes the \bold{fett and \italic{kursiv}} \italic{text}.

This text is \style(fontWeight=700){bold}. It has no
newline problem.

Now something in \red{RED}, with \underline{underline} and with \strike{strike out}.
Futhermore, we can write \tt{typewriter}.

- First, do this. Take note that this block does now feature a hanging indent, such that it looks left aligned.
 - A new enum
 - At an indented level
- Second, do that

\p\bold A new paragraph with a command in front.
\h1\color(0, 0, 255) All blue
\h1\red All red

The text \red from here on is red, because of `\red`.

\h2\margin(20, 20, 20, 20) With extra margin
\h2\margin(left=20*mm, right=20*mm) Left right margin
\h2\center More in the center

As we have shown in \ref("intro"), ours is the best.

\chapter\lobster\label("intro") In Lobster with g
\chapter \lobster In Lobster with more g
\subchapter \red This is a sub-chapter
\chapter\roboto In Roboto with g.
\chapter\roboto In Roboto with \bold{bold g}.