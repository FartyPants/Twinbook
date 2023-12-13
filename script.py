import gradio as gr
import modules.shared as shared
from pathlib import Path
import re
import json
import time
import html
import copy
from functools import partial
from modules.text_generation import stop_everything_event
from modules import chat
from modules import ui as main_ui
from modules.utils import gradio
from modules.extensions import apply_extensions
import random

right_symbol = '\U000027A1'
left_symbol = '\U00002B05'
refresh_symbol = '\U0001f504'  # 🔄

basepath = "extensions/Twinbook/last.json"
last_undo =''

describe_all = "Add an immersive and evocative description to the scene, capturing its visual and auditory aspects."
describe_auditory = "Can you help me create a more evocative description of the scene, capturing its auditory aspects??"
describe_smell = "Can you help me create a more evocative description of the scene, capturing its olfactory aspects?"
describe_paint = "Paint a vivid picture to make the story come alive for the reader."
describe_va = "Add auditory and visual imagery to the paragraph to create a more vivid picture for the reader."
# You are a talented writing assistant. Always respond by incorporating the instructions into expertly written prose that is highly detailed, evocative, vivid and engaging.


describe_add_simile = "Please enhance the sentence with a simile."
# postfix can be also comma delimited
simile_postfix = 'like'
postfix_index = 0

save_params = {
    "text_boxA": '',
    "text_boxB": '',
    "text_boxC": '',
    "context_replace": '',
    "extra_context": '',
    "extra_prefix": '',
    "add_stats": False,
}



params = {
        "display_name": "Twinbook",
        "is_tab": True,
        "selectA": [0,0],
}

class ToolButton(gr.Button, gr.components.FormComponent):
    """Small button with single emoji as text, fits inside gradio forms"""

    def __init__(self, **kwargs):
        super().__init__(variant="tool", **kwargs)

    def get_block_name(self):
        return "button"


def create_refresh_button(refresh_component, refresh_method, refreshed_args, elem_class):
    def refresh():
        refresh_method()
        args = refreshed_args() if callable(refreshed_args) else refreshed_args

        for k, v in args.items():
            setattr(refresh_component, k, v)

        return gr.update(**(args or {}))

    refresh_button = ToolButton(value=refresh_symbol, elem_classes=elem_class)
    refresh_button.click(
        fn=refresh,
        inputs=[],
        outputs=[refresh_component]
    )
    return refresh_button


def read_file_to_string(file_path):
    data = ''
    try:
        with open(file_path, 'r') as file:
            data = file.read()
    except FileNotFoundError:
        data = ''

    return data


def atoi(text):
    return int(text) if text.isdigit() else text.lower()

def save_string_to_file(file_path, string):
    try:
        with open(file_path, 'w') as file:
            file.write(string)
        print("String saved to file successfully.")
    except Exception as e:
        print("Error occurred while saving string to file:", str(e))


last_history_visible = []
last_history_internal = []


def send_selected_to_Keep(text, textC):
    global params
    global save_params
    selF = params['selectA'][0]
    selT = params['selectA'][1]
    params['selectA'] = [0,0]
    texttextOUT = str(text)
    if not selF==selT:
        print(f"\033[1;32;1m\nSending selected text to Keep\033[0;37;0m")
        texttextOUT = texttextOUT[selF:selT]

        rettext = str(textC)+"\n+++\n"+texttextOUT+"\n"
        save_params["text_boxC"] = rettext
        return rettext
    else:
        print(f"No selection made")
        save_params["text_boxC"] = textC
        return textC


def filter_squigly(text):
    text = text.replace('\r\n','\n')
    lines = text.split('\n')
    result = ''
    for line in lines:
        if line.startswith('~~~~'):
            line = '~~~~'
        
        if result == '':
            result = line
        else:    
            result += '\n' + line

    return result
    
# bastardized original chat function
# chat.py
def generate_reply_wrapperMY(question, textBoxB, context_replace, extra_context, extra_prefix, state, quick_instruction, _continue=False, _genwithResponse = False, _continue_sel = False, _postfix = '', _addstop = []):

    global params
    global last_history_visible
    global last_history_internal
    global last_undo
    global postfix_index
    global basepath
    
    selF = params['selectA'][0]
    selT = params['selectA'][1]
 
    params['selectA'] = [0,0]
   
    texttextOUT = str(textBoxB)
    
    text_before = ""
    text_after = ""

    if _continue_sel:
        if not selF==selT:
            print(f"\033[1;32;1m\nContinue from selected text and inserting after {selT}\033[0;37;0m")
            text_before = texttextOUT[:selF]
            text_after = texttextOUT[selT:]
            texttextOUT = texttextOUT[selF:selT]
        else:
            print(f"\033[1;31;1m\nNo selection made, reverting to full text Continue\033[0;37;0m")
            _continue_sel = False
 


    last_undo = text_before + texttextOUT + text_after
    visible_text = None

    text = question



    if extra_prefix.strip()!='':
        text = extra_prefix + question

    if quick_instruction.strip()!='':
        text = quick_instruction

    if _postfix !='':
        string_list = [item.strip() for item in _postfix.split(',')]
        if len(string_list) > 0:
            postfix_index = int(postfix_index) % len(string_list)
            next_item = string_list[postfix_index]
            postfix_index = postfix_index + 1
            texttextOUT = texttextOUT.rstrip() 
            texttextOUT = texttextOUT + ' ' + next_item

    textB = texttextOUT

    if state['turn_template']=='':
        print("Instruction template is empty! Select Instruct template in tab [Parameters] - [Instruction Template]")
        textB = texttextOUT + "\n Instruction template is empty! Select Instruct template in tab [Parameters] - [Instruction template]"
        yield text_before + textB + text_after
        return


    state['mode'] = 'instruct'
    
    _iswriting = "..."

    if text_after!='':
        _iswriting = "[...]"

    #context = state['context']

    context_instruct = state['context_instruct']
    contest_instruct_bk = context_instruct

    if context_replace.strip()!='':
        context_instruct = context_replace+'\n'
        state['context_instruct'] = context_instruct
    
    if extra_context.strip()!='':
        state['context_instruct'] = extra_context+ '\n' + context_instruct


    state = apply_extensions('state', state)
    if shared.model_name == 'None' or shared.model is None:
        print("No model is loaded! Select one in the Model tab.")
        yield text_before + textB + text_after
        return
    
    output = {'visible': [], 'internal': []}    
    output['internal'].append(['', ''])
    output['visible'].append(['', ''])

    last_history = {'visible': [], 'internal': []} 
    stopping_strings = chat.get_stopping_strings(state)

    if len(_addstop) > 0:
        stopping_strings = stopping_strings + _addstop


    print (stopping_strings)
    is_stream = state['stream']
    regenerate = False

   


  # Prepare the input
    if not any((regenerate, _continue)):
        visible_text = text

        add_stats = save_params["add_stats"]

        if add_stats:
            if shared.model:
                adapter_name = getattr(shared.model,'active_adapter','')

                suffix_models = shared.model_name
                if adapter_name != '':
                    suffix_models = suffix_models + " [" + adapter_name+ "]" 


                suffix_models =  suffix_models + f"  Temp: {state['temperature']}, top_p: {state['top_p']}, top_k: {state['top_k']}, RP: {state['repetition_penalty']}"

            if texttextOUT!='':
                textB = texttextOUT + f"\n\n~~~~ {suffix_models} ~~~~\n\n"
        else:
            if texttextOUT!='':
                textB = texttextOUT + f"\n\n~~~~\n\n"


        # Apply extensions
        text, visible_text = apply_extensions('chat_input', text, visible_text, state)
        text = apply_extensions('input', text, state, is_chat=True)

        outtext = text_before + textB + _iswriting + text_after
        yield outtext

    else:
        visible_text = text 

     
        if regenerate:
            output['visible'].pop()
            output['internal'].pop()
            outtext = text_before + textB + _iswriting  + text_after

            yield outtext

        elif _continue:

            textB = texttextOUT
            # continue sel can span across squiglies
            if _continue_sel:
                last_part = texttextOUT
                filtered = filter_squigly(last_part)
                last_part = filtered.replace("\n~~~~\n",'') 

            else: 

                filtered = filter_squigly(texttextOUT)   
                parts = filtered.split('~~~~')
                # Extract the last part (after the last "~~~~")
                if len(parts) > 0:
                    last_part = parts[-1].strip()
                else:
                    last_part = ''
            # fill history for generate_chat_prompt
            last_history['internal'].append([text, last_part])
            last_history['visible'].append([text, last_part])

            outtext = text_before + textB + _iswriting + text_after   
            yield outtext


        # Generate the prompt
    kwargs = {
        '_continue': _continue,
        'history': last_history,
    }

    #prompt = apply_extensions('custom_generate_chat_prompt', question, state, **kwargs)
    
    prompt = chat.generate_chat_prompt(text, state, **kwargs)

    if _genwithResponse:

        filtered = filter_squigly(texttextOUT)   
        parts = filtered.split('~~~~')

        # Extract the last part (after the last "~~~~")
        if len(parts) > 0:
            last_part = parts[-1].strip()
        else:
            last_part = ''

        if last_part != '':
            prompt = last_part+"\n\n"+prompt



    #put it back, just in case
    state['context_instruct'] = contest_instruct_bk

    # Generate
    reply = None
    for j, reply in enumerate(chat.generate_reply(prompt, state, stopping_strings=stopping_strings, is_chat=True)):

        visible_reply = re.sub("(<USER>|<user>|{{user}})", state['name1'], reply)
        
        if shared.stop_everything:
            output['visible'][-1][1] = apply_extensions('output', output['visible'][-1][1], state, is_chat=True)

            output_text = output['visible'][-1][1]
            yield  text_before + textB + output_text + text_after
            return

        if _continue:
            output['internal'][-1] = [text,  reply]
            output['visible'][-1] = [visible_text, visible_reply]
            if is_stream:
                output_text = output['visible'][-1][1]
                yield text_before + textB + output_text  + text_after
        elif not (j == 0 and visible_reply.strip() == ''):
            output['internal'][-1] = [text, reply.lstrip(' ')]
            output['visible'][-1] = [visible_text, visible_reply.lstrip(' ')]

            if is_stream:
                output_text = output['visible'][-1][1]
                yield  text_before + textB + output_text + text_after

    output['visible'][-1][1] = apply_extensions('output', output['visible'][-1][1], state, is_chat=True)
    
    output_text = output['visible'][-1][1]
    
    # not really used for anything
    last_history_visible = output['visible'][-1]
    last_history_internal = output['internal'][-1]

 

    save_params["text_boxA"] = question
    save_params["text_boxB"] = text_before + textB + output_text + text_after
    #save_params["text_boxC"] = textBoxC
    save_params["context_replace"] =  context_replace
    save_params["extra_context"] = extra_context
    save_params["extra_prefix"] =  extra_prefix


    try:
        with open(Path(basepath), 'w') as json_file:
            json.dump(save_params, json_file, indent=4)
    except:
        print("Can't save last state..")

    yield  text_before + textB + output_text + text_after

def custom_js():
    java = '''
const polybookElement = document.querySelector('#textbox-polybook textarea');
let polybookScrolled = false;

polybookElement.addEventListener('scroll', function() {
  let diff = polybookElement.scrollHeight - polybookElement.clientHeight;
  if(Math.abs(polybookElement.scrollTop - diff) <= 1 || diff == 0) {
    polybookScrolled = false;
  } else {
    polybookScrolled = true;
  }
});

const polybookObserver = new MutationObserver(function(mutations) {
  mutations.forEach(function(mutation) {
    if(!polybookScrolled) {
      polybookElement.scrollTop = polybookElement.scrollHeight;
    }
  });
});

polybookObserver.observe(polybookElement.parentNode.parentNode.parentNode, config);

'''
    return java


help_str = """
## Mini Guide
It looks simple. It works simple. But this is a great way of combining Instruction Chat with Notebook. You get two huge text boxes! On the left, for typing INSTRUCTIONS; on the right, for RESPONSE. 

So what, huh? Well, read on.

### Generate NEW, edit response, then CONTINUE
Here's how it works. Type 'What's your name?' into the Instructions box and click GENERATE NEW. That prints something like *'My name is Assistant'* into the right Response box.

Oh, but you can type into the Response box as well, just like in the Notebook. For instance, you might delete the period and type *' and I like '*. Then when you click CONTINUE, it goes on generating more text. Probably how it really likes to help users answering their questions.

So far so good. But hey! Did you realize you could have also changed the INSTRUCTIONS itself before you hit Continue! Let's say, *'Describe how you enjoy your ice-cream.'* And then hit CONTINUE.

See? Suddenly it talks about ice cream, It uses the previous response plus the new instruction to CONTINUE generating the text.

This way you can modify responses, in the middle of the text - sort of steer the LLM towards your goal. It's like a chat where you control both sides of the discussion. 

### Generate New
Every time you click GENERATE NEW, it inserts those little squiggly lines (separator) into the Response window before it starts writing. 
Then it comes up with a whole NEW bit of text following the Instruction that doesn't depend on any previous Responses. 
Unlike the chat that will include all the previous questions and answer, Generate NEW is a new start from blank slate but without clearing the text in Response window. 

The squigglies are separating the different NEW responses (sort of like alternative takes). 
And Continue will always only take to account the text after the last squiggly. So removing squigglies, pasting your own text, editing the text - all those things will affect the Continue operation.

### Gen with Memory
This function takes the last Response (i.e., after last Squiggly line, just like CONTINUE), and inserts it at the top of the LLM instruction, before System or Instruction commands. This means that the LLM gets to see the last response, but only as a memory. So it generates a NEW response, not a continuation of the text (like CONTIUE does), but with a faint remote ideas of previous facts.

So if you tell it to just write and story (Generate NEW) it will write a random story and then if you use Generate NEW again the next story will be different. However if you use Gen with Memory, the story could be somehow simillar to the last generated one.

### Continue [SEL] (insert after selection)
If you select a text in Response textbox, you can use Continue [SEL] to continue generating text and insert it after the selected text. The text will be generated from the selected text with the instructions in the INSTRUCTION box. Very cheeky.
Also selection CAN span multiple blocks (squigglies) and all the text will be used to generate Continue.

Ugh, I know, it sounds complicated when you try to describe like this. You need to figure out how it works. It makes sense. I pinky swear.
"""



def ui():
    global params
    global basepath
    global save_params

    params['selectA'] = [0,0]

    try:
        with open(basepath, 'r') as json_file:
            new_params = json.load(json_file)
            print("Twinbook: Loading last state")
            for item in new_params:
                save_params[item] = new_params[item]
    except:
        print("Twinbook: No last state saved")
        pass

    with gr.Row():
        with gr.Column():
            #extra_context = gr.Textbox(value='', lines=5, label = 'Extra Context', elem_classes=['textbox'])
            with gr.Tab('Instructions'):
                text_boxA = gr.Textbox(value=save_params["text_boxA"], lines=20, label = '', elem_classes=['textbox', 'add_scrollbar'])
            with gr.Tab('Extra Context'):
                quick_instruction = gr.Textbox(value='', lines=5, label = 'Temporary, ALT Instruction', elem_classes=['textbox'], info='Enter an Alternative instruction that will temporarily take precedent over the main Instruction. Example: "Describe xxx in details" to add more context to a paragraph selected in Response box, while using Continue [SEL].')
                gr.Markdown('Select Text in right window and press one of the Quick Instructions')
                with gr.Row():
                    button_describe_all = gr.Button('Immersive description')
                    button_describe_va = gr.Button('Vivid Imagery')
                    button_describe_paint = gr.Button('Vivid Picture')
                    button_describe_auditory = gr.Button('Auditory Senses')
                    button_describe_smell = gr.Button('Senses of Smell')
                    button_describe_simile = gr.Button('Simile')

                extra_context = gr.Textbox(value=save_params["extra_context"], lines=5, label = 'Extra Context and Memories', elem_classes=['textbox'], info='Enter memories that the model should know. Example: Your name is Sarah and you are a student at UBC')
                context_replace =  gr.Textbox(value=save_params["context_replace"], lines=1, label = 'System Instruction', elem_classes=['textbox'], info='If filled, it will replace the Instruct Template system instruction.', placeholder = 'Below is an instruction that describes a task, you are blah, blah, blah...')
                extra_prefix = gr.Textbox(value=save_params["extra_prefix"], lines=2, label = 'Instruction Prefix', elem_classes=['textbox'], info='Enter instruction that will be always inserted before your text in the prompt. Example: Rewrite the following text: ')
                with gr.Row():
                    button_prefix_rewrite = gr.Button('Rewrite')
                    gr.Markdown(" ")
                    gr.Markdown(" ")
                    gr.Markdown(" ")
                    button_prefix_clear = gr.Button('Clear')
                with gr.Row():
                    add_stats =  gr.Checkbox(value = save_params["add_stats"], label='Show Stats in divider',info = 'Add model, lora and parameters after ~~~~ ' )    

            with gr.Tab('Help'):
                gr.Markdown(help_str)
                 
        with gr.Column():
            with gr.Tab('Response'):
                text_boxB = gr.Textbox(value=save_params["text_boxB"], lines=20, label = '', elem_classes=['textbox', 'add_scrollbar'], elem_id='textbox-polybook')
            with gr.Tab('Keep'):
                text_boxC = gr.Textbox(value=save_params["text_boxC"], lines=20, label = '', elem_classes=['textbox', 'add_scrollbar'], elem_id='textbox-polybook')
                               
    with gr.Row():    
        with gr.Column():      
            with gr.Row():
                with gr.Column():
                    with gr.Row():    
                        generate_btn = gr.Button('Generate New', variant='primary')
                        generate_btnR = gr.Button('Gen with memory', variant='primary', elem_classes="small-button")
                        #generate_Sel = gr.Button('Generate [SEL]', variant='primary', elem_classes="small-button")
                        stop_btn = gr.Button('Stop', elem_classes="small-button")
                #with gr.Column():
                #    with gr.Row():    
                #        mode = gr.Radio(label='Use Template', choices=['Chat', 'Instruction'], value='Instruction', elem_classes='slim-dropdown')

        with gr.Column():
            with gr.Row():
                with gr.Column():
                    with gr.Row():    
                        continue_btn =  gr.Button('Continue', variant='primary')
                        continue_btn_sel = gr.Button('Continue [SEL]',variant='primary', elem_classes="small-button")
                        stop_btn2 = gr.Button('Stop', elem_classes="small-button")
                        clear2 = gr.Button('Clear', elem_classes="small-button")    
                        undo = gr.Button('Undo/Redo', elem_classes="small-button")
                        send_sel_keep = gr.Button('[Sel] to Keep', elem_classes="small-button")     


    input_paramsA = [text_boxA, text_boxB, context_replace, extra_context, extra_prefix, shared.gradio['interface_state'], quick_instruction]
    input_paramsQI = [text_boxA, text_boxB, context_replace, extra_context, extra_prefix, shared.gradio['interface_state']]
    output_paramsA =[text_boxB]

    def clear_quick_instruction(quick_instruction):
        return ''

    generate_btn.click(
        main_ui.gather_interface_values, gradio(shared.input_elements), gradio('interface_state')).then(
        generate_reply_wrapperMY, inputs=input_paramsA, outputs= output_paramsA, show_progress=False).then(clear_quick_instruction,quick_instruction,quick_instruction)

    continue_btn.click(
        main_ui.gather_interface_values, gradio(shared.input_elements), gradio('interface_state')).then(
        partial(generate_reply_wrapperMY, _continue=True), inputs=input_paramsA, outputs= output_paramsA, show_progress=False).then(clear_quick_instruction,quick_instruction,quick_instruction)
    
    continue_btn_sel.click(
        main_ui.gather_interface_values, gradio(shared.input_elements), gradio('interface_state')).then(
        partial(generate_reply_wrapperMY, _continue=True, _genwithResponse = False, _continue_sel = True), inputs=input_paramsA, outputs= output_paramsA, show_progress=False).then(
            clear_quick_instruction,quick_instruction,quick_instruction)
    
    generate_btnR.click(
        main_ui.gather_interface_values, gradio(shared.input_elements), gradio('interface_state')).then(
        partial(generate_reply_wrapperMY, _continue=False, _genwithResponse = True), inputs=input_paramsA, outputs= output_paramsA, show_progress=False).then(clear_quick_instruction,quick_instruction,quick_instruction)

    
    button_describe_all.click(main_ui.gather_interface_values, gradio(shared.input_elements), gradio('interface_state')).then(
        partial(generate_reply_wrapperMY, quick_instruction = describe_all ,_continue=True, _genwithResponse = False, _continue_sel = True,_addstop = ['\n']), inputs=input_paramsQI, outputs= output_paramsA, show_progress=False)

    button_describe_va.click(main_ui.gather_interface_values, gradio(shared.input_elements), gradio('interface_state')).then(
        partial(generate_reply_wrapperMY, quick_instruction = describe_va ,_continue=True, _genwithResponse = False, _continue_sel = True,_addstop = ['\n']), inputs=input_paramsQI, outputs= output_paramsA, show_progress=False)
 
    button_describe_paint.click(main_ui.gather_interface_values, gradio(shared.input_elements), gradio('interface_state')).then(
        partial(generate_reply_wrapperMY, quick_instruction = describe_paint ,_continue=True, _genwithResponse = False, _continue_sel = True,_addstop = ['\n']), inputs=input_paramsQI, outputs= output_paramsA, show_progress=False)
    
    button_describe_auditory.click(main_ui.gather_interface_values, gradio(shared.input_elements), gradio('interface_state')).then(
        partial(generate_reply_wrapperMY, quick_instruction = describe_auditory ,_continue=True, _genwithResponse = False, _continue_sel = True,_addstop = ['\n']), inputs=input_paramsQI, outputs= output_paramsA, show_progress=False)
    
    button_describe_smell.click(main_ui.gather_interface_values, gradio(shared.input_elements), gradio('interface_state')).then(
        partial(generate_reply_wrapperMY, quick_instruction = describe_smell ,_continue=True, _genwithResponse = False, _continue_sel = True,_addstop = ['\n']), inputs=input_paramsQI, outputs= output_paramsA, show_progress=False)

    button_describe_simile.click(main_ui.gather_interface_values, gradio(shared.input_elements), gradio('interface_state')).then(
        partial(generate_reply_wrapperMY, quick_instruction = describe_add_simile ,_continue=True, _genwithResponse = False, _continue_sel = True, _postfix = simile_postfix, _addstop = ['.','!','?']), inputs=input_paramsQI, outputs= output_paramsA, show_progress=False)
                
    stop_btn.click(stop_everything_event, None, None, queue=False)
    stop_btn2.click(stop_everything_event, None, None, queue=False)
    
    def cleartext(texttextOUT):
        global last_undo

        if texttextOUT=='':
            return ''

        last_undo = str(texttextOUT)
        
        return ''

    clear2.click(cleartext, text_boxB, text_boxB, show_progress=False)

    def undo_event(texttextOUT):
        global last_undo

        prev_undo = last_undo
        last_undo = str(texttextOUT)
        return prev_undo


    undo.click(undo_event, text_boxB, text_boxB, show_progress=False)

    def on_selectA(evt: gr.SelectData):  # SelectData is a subclass of EventData
        #print (f"Continue [SEL] is available for selected text {evt.index}")
        global params
        params['selectA'] = evt.index
        return ""
    
    text_boxB.select(on_selectA, None, None)

    send_sel_keep.click(send_selected_to_Keep, [text_boxB,text_boxC], text_boxC, show_progress=False)

    text_boxC.change(lambda x: save_params.update({"text_boxC": x}), text_boxC, None) 
    add_stats.change(lambda x: save_params.update({"add_stats": x}), add_stats, None)


    def rewrite_prefix(text: str):
        return text

    button_prefix_rewrite.click(partial(rewrite_prefix, text="Rewrite the following text: "), None, extra_prefix, show_progress=False)
    button_prefix_clear.click(partial(rewrite_prefix, text=""), None, extra_prefix, show_progress=False)
