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

right_symbol = '\U000027A1'
left_symbol = '\U00002B05'
refresh_symbol = '\U0001f504'  # 🔄


last_undo =''


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

def get_file_path(folder, filename):
    basepath = "extensions/mass_rewritter/"+folder
    #print(f"Basepath: {basepath} and {filename}")
    paths = (x for x in Path(basepath).iterdir() if x.suffix in ('.txt'))
    for path in paths:
        if path.stem.lower() == filename.lower():
            return str(path)
    return ""

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

def generate_reply_wrapperMY_SEL(question, textBoxB, context_replace, extra_context, extra_prefix, state, _continue=False, _genwithResponse = False):
    global params
    global last_undo

    texttextOUT = str(textBoxB)

    selF = params['selectA'][0]
    selT = params['selectA'][1]
    if not selF==selT:
        print(f"\033[1;32;1m\nContinue from selected text and inserting after {selT}\033[0;37;0m")
        params['selectA'] = [0,0]
        beforeB = texttextOUT[:selF]
        currentB = texttextOUT[selF:selT]
        afterB = texttextOUT[selT:]
    else:
        currentB = texttextOUT
        params['selectA'] = [0,0]
        beforeB = ""
        afterB = ""
        print(f"\033[1;31;1m\nNo selection made, reverting to full text Continue\033[0;37;0m") 
        
    return generate_reply_wrapperMY(question, currentB, context_replace, extra_context, extra_prefix, state,_continue=True, _genwithResponse = False, text_before=beforeB, text_after=afterB)


# bastardized original chat function
# chat.py
def generate_reply_wrapperMY(question, textBoxB, context_replace, extra_context, extra_prefix, state, _continue=False, _genwithResponse = False, _continue_sel = False):

    global params
    global last_history_visible
    global last_history_internal
    global last_undo
    
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

    #print (stopping_strings)
    is_stream = state['stream']
    regenerate = False

   


  # Prepare the input
    if not any((regenerate, _continue)):
        visible_text = text

        if texttextOUT!='':
            textB = texttextOUT + "\n\n~~~~\n\n"

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
                last_part = last_part.replace("\n~~~~\n",'') 
            else:    
                parts = texttextOUT.split('~~~~')
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
        parts = texttextOUT.split('~~~~')

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

    params['selectA'] = [0,0]

    with gr.Row():
        with gr.Column():
            #extra_context = gr.Textbox(value='', lines=5, label = 'Extra Context', elem_classes=['textbox'])
            with gr.Tab('Instructions'):
                text_boxA = gr.Textbox(value='', lines=20, label = '', elem_classes=['textbox', 'add_scrollbar'])
            with gr.Tab('Extra Context'):
                extra_context = gr.Textbox(value='', lines=10, label = 'Extra Context', elem_classes=['textbox'], info='Enter memories that the model should know. Ex: Your name is Sarah.')
                context_replace =  gr.Textbox(value='', lines=1, label = 'System Instruction', elem_classes=['textbox'], info='If not empty, it will replace the default system instruction (Such as "Below is an instruction that describes a task...")')
                extra_prefix = gr.Textbox(value='', lines=2, label = 'Extra instruction', elem_classes=['textbox'], info='Enter extra instruction that will be inserted before your text in the prompt. Ex: Rewrite the following text: ')
            with gr.Tab('Help'):
                gr.Markdown(help_str)
                 
        with gr.Column():
            with gr.Tab('Response'):
                text_boxB = gr.Textbox(value='', lines=20, label = '', elem_classes=['textbox', 'add_scrollbar'], elem_id='textbox-polybook')
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


    input_paramsA = [text_boxA, text_boxB, context_replace, extra_context, extra_prefix, shared.gradio['interface_state']]
    output_paramsA =[text_boxB]

    generate_btn.click(
        main_ui.gather_interface_values, gradio(shared.input_elements), gradio('interface_state')).then(
        generate_reply_wrapperMY, inputs=input_paramsA, outputs= output_paramsA, show_progress=False)

    continue_btn.click(
        main_ui.gather_interface_values, gradio(shared.input_elements), gradio('interface_state')).then(
        partial(generate_reply_wrapperMY, _continue=True), inputs=input_paramsA, outputs= output_paramsA, show_progress=False)
    
    continue_btn_sel.click(
        main_ui.gather_interface_values, gradio(shared.input_elements), gradio('interface_state')).then(
        partial(generate_reply_wrapperMY, _continue=True, _genwithResponse = False, _continue_sel = True), inputs=input_paramsA, outputs= output_paramsA, show_progress=False)
    
    generate_btnR.click(
        main_ui.gather_interface_values, gradio(shared.input_elements), gradio('interface_state')).then(
        partial(generate_reply_wrapperMY, _continue=False, _genwithResponse = True), inputs=input_paramsA, outputs= output_paramsA, show_progress=False)

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
        print (f"Continue [SEL] is available for selected text {evt.index}")
        global params
        params['selectA'] = evt.index
        return ""
    
    text_boxB.select(on_selectA, None, None)
