# Digi4K

## The Goal
Create a competent Friday Night Funkin'-style engine in Pygame. Might be intergrated into Charm at some point if it's adaptable and good enough.

An example of FNF gameplay can be found [here.](https://www.youtube.com/watch?v=IK6-kJpqed4)

## The Plan

* Have a nice-to-play 4K engine.
  * Accuracy is considered; timing window currently unknown but score is affected by your closeness to ±0ms.
  * Has an HP-system. (See **HP.**)
  * Holding a sustain note gives you more score and HP, releasing it early loses you HP
  * Losing all your HP ends the game.
* Have a Player 2 AI.
  * Chart displays on the left and is automatically played.
  * The opponents notes can cause effects (see **Effects.**)
* Look visually accurate (and improved) to FNF.

### Chart Reading
* Able to parse the (annoyingly structured) `.jsons` FNF uses.
* Able to parse a much nice format I make.

### HP
* The HP bar starts at 50%.
* Hitting notes fills your bar 1/Xth, dictated by the chart and some **Events.**
* Missing notes removes 1/Xth of your HP, dictated by the chart and some **Events.**

### Events
There are multiple chart events that can happen throughout the song, including:

* Changing HP drain
* Changing HP gain
* Setting how much opponent's notes hurt you
* Setting how much damage bomb notes do
* Set BPM
* Various **Animations.**
  * Camera movements
  * Character animations
  * Froeground/background animations

### Animations
Animations are a key part of FNF, and hence, will be important in this recreation/engine.

* The characters play different animations when you hit the up, down, left, or right notes.
* The characters play an animation when they miss a note.
* The characters have idle animations.
* The center character (often GF) vibes to the BPM of the song.
* The camera pulses slightly to the beat.
* The camera pans between characters according to Events.
* Animations can play in the background and foreground [over the play field].

## Improvments over FNF

* Lyric support
* More events [instead of the external `modchart.lua` some engines are using...]
