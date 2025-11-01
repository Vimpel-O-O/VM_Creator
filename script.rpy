default game_continues = True
default countt = 1
default current_scene = "start"   # 👈 define it once
init python:
    # right now it just stores the next scene id
    def advance_story(next_scene_id):
        store.current_scene = next_scene_id

init:
    # 1. FIX: DEFINE THE MAIN BUTTON STYLE (my_fancy_button)
    # This style is required because your textbuttons reference it.
    style my_fancy_button is button:
        # Example style: dark gray background, no padding change
        idle_background Solid("#444444") 
        hover_background Solid("#666666")
        padding (40, 15, 40, 15)
        
    # 2. Define the text properties for that button (This was already correct)
    style my_fancy_button_text is button_text:
        idle_color "#FFFFFF"
        hover_color "#FFFF00"
        size 30
        outlines [(1, "#000000", 0, 0)]



define e = Character("Eileen")
image ai_image =  "image01.jpg"

label game_loop:
    # show your AI choice screen every time
    call screen ai_choice_screen
    return



screen ai_choice_screen():

    # Full-screen background
    add "image01.jpg" xpos 0 ypos 0 xsize config.screen_width ysize config.screen_height

    # Question text
    text "You find yourself at a crossroads. Which path will you take?" xpos 0.5 ypos 0.1 xanchor 0.5 yanchor 0.5 size 40 color "#FFFFFF" outlines [(0.5, "#000000", 0, 0)]

    # Choice buttons
    vbox:
        spacing 20
        xalign 0.5
        yalign 0.8

        textbutton "Next" action [Hide("ai_choice_screen"), Jump("left_path")]:
            # This is correct placement:
            style "my_fancy_button" 

    #     textbutton "Take the Right Path" action [Hide("ai_choice_screen"), Jump("right_path")]:
    #         # This is also correct placement:
    #         style "my_fancy_button"



label left_path:
    e "You chose the left path!"

    if game_continues:            # 👈 no 'store.' needed
        # $ advance_story("scene_A")
        jump game_loop            # 👈 go back to the loop
    else:
        e "This path leads to an abrupt end."
        return




label start:
    jump game_loop
