# Twinbook

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/Q5Q5MOB4M)


New:
- Fix: Working with the most recent WebUI that removed the Instruct template and added jinja
- Show Stats in divider (add model, lora and params after ~~~~ (optional settings in Extra context tab)
- save state of the tect boxes so when it reloads, the text is back

It looks simple. It works simple. But this is a great way of combining Instruction Chat with Notebook. You get two huge text boxes! On the left, for typing INSTRUCTIONS; on the right, for RESPONSE.

So what, huh? Well, read on.

Here’s how it works. Type ‘What’s your name?’ into the Instructions box and click GENERATE NEW. That prints something like ‘My name is Assistant’ into the right Response box.

![image](https://github.com/FartyPants/Twinbook/assets/23346289/70374ba9-7d9b-4a5f-8f4e-598c7de13ed7)

Oh, but you can type into the Response box as well, just like in the Notebook. For instance, you might delete the period and type ’ and I like ’. 
Then when you click CONTINUE, it goes on generating more text. Probably how it really likes to help users answering their questions.

![image](https://github.com/FartyPants/Twinbook/assets/23346289/7fc2e935-4653-494a-a1f9-5127a2e223be)

So far so good. But hey! Did you realize you could have also changed the INSTRUCTIONS itself before you hit Continue! Let's say, ‘Describe how you enjoy your ice-cream.’ And then hit CONTINUE. 

![image](https://github.com/FartyPants/Twinbook/assets/23346289/c9a37f42-0c90-4fc5-92c0-ebbbe5aa6098)

See? Suddenly it talks about ice cream, It uses the previous response plus the new instruction to CONTINUE generating the text. 

This way you can modify responses, in the middle of the text - sort of steer the LLM towards your goal. It’s like a chat where you control both sides of the discussion. Just delete the part where it gets off the ramp and write different instructions. Both the previus text and the new instruction will became part of the new text.

![image](https://github.com/FartyPants/Twinbook/assets/23346289/48ef3975-518a-4cce-820e-0ea9f960d83e)

## GENERATE NEW
Every time you click GENERATE NEW, it inserts those little squiggly lines (separator) into the Response window before it starts writing. Then it comes up with a whole NEW bit of text following the Instruction that doesn’t depend on any previous Responses. Unlike the chat that will include all the previous questions and answer, Generate NEW is a new start from blank slate but without clearing the text in Response window. Just adding squiggly line and writing new response.

![image](https://github.com/FartyPants/Twinbook/assets/23346289/c1cd16fc-f147-4d1d-8903-00d4dab50210)

The squigglies are separating the different NEW responses (sort of like alternative takes). And Continue will always only take to account the text after the last squiggly. So removing squigglies, pasting your own text, editing the text - all those things will affect the Continue operation.

## GEN WITH MEMORY
This function takes the last Response (i.e., after last Squiggly line, just like CONTINUE), and inserts it at the top of the LLM instruction, before System or Instruction commands. This means that the LLM gets to see the last response, but only as a memory. So it generates a NEW response, not a continuation of the text (like CONTIUE does), but with a faint remote ideas of previous facts. 

So if you tell it to just write and story (Generate NEW) it will write a random story and then if you use Generate NEW again the next story will be different. However if you use Gen with Memory, the story could be somehow simillar to the last generated one.

## Continue [SEL] (insert after selection)
If you select a text in Response textbox, you can use Continue [SEL] to continue generating text and insert it after the selected text. The text will be generated from the selected text with the instructions in the INSTRUCTION box. Very cheeky.
Also selection CAN span multiple blocks (squigglies) and all the text will be used to generate Continue.

## Keep
Keep is a box where you can keep stuff. You can also send text from Response to keep with one button. Just select text in Response window and click [sel] to Keep

Ugh, I know, it sounds complicated when you try to describe like this. You need to figure out how it works. It makes sense. I pinky swear.

---

### **Twinbook: User Guide**

The 'Twinbook' extension offers a unique and highly interactive way to work with your AI model, blending the "instruct" mode with a flexible "notebook" style text editor. It's designed for users who want granular control over their creative writing or content generation process, allowing for iterative editing, targeted regeneration, and a persistent memory of your work.

Think of it as a collaborative writing environment where you provide instructions, the AI generates text, and you can instantly edit, refine, or guide the AI's continuation, all within two large, linked text areas.

---

### **1. The Core Workflow: Generate, Edit, Continue**

Twinbook's power lies in its fluid three-step process:

1.  **Generate NEW:** Provide a new instruction, and the AI will generate a fresh piece of text, creating a new "block" of content in the Response area.
2.  **Edit the Response:** Directly modify, delete, or add text anywhere within the AI's generated response. This is where you manually steer the narrative or correct errors.
3.  **CONTINUE:** Based on your current instruction and the *last section* of text in the Response area (especially useful after editing), the AI will seamlessly continue writing.

This loop allows you to steer the AI's output, refine its style, or introduce new elements into your story or document in real-time.

---

### **2. Main Interface Areas**

The Twinbook interface is split into two primary columns, each with dedicated tabs:

#### **A. Left Column: Your Instructions & Control Panel**

This side is where you tell the AI what to do.

*   **Instructions Tab (`text_boxA`):**
    *   **How to Use:** Type your main instruction for the AI here. This is the primary prompt for "Generate New" and influences "Continue" operations.
    *   **What it Does:** This text is sent to the LLM to guide its generation.

*   **Extra Context Tab (Accordion of advanced settings):** This tab provides powerful ways to refine the AI's behavior.
    *   **Temporary, ALT Instruction (`quick_instruction`):**
        *   **How to Use:** Enter a *temporary* instruction here (e.g., "Describe the scene in vivid detail"). This will override the main "Instructions" box for the *next single generation*. It automatically clears after use.
        *   **Use Case:** Ideal for quick, one-off commands like "Summarize the above" or "Make this sentence more dramatic" without changing your main instruction.
    *   **Quick Enhancements Buttons:** A set of pre-defined "Temporary, ALT Instructions" for common creative tasks.
        *   **How to Use:** Select some text in the "Response" box (or ensure your cursor is at the end of the desired block), then click one of these buttons. They automatically populate the "Temporary, ALT Instruction" and trigger a "Continue [SEL]" action.
        *   **Options:** `Description`, `Visual`, `Vivid Picture`, `Sound`, `Smell`, `Simile`, `Write more`.
        *   **What it Does:** These provide common prompts to expand or modify a selected piece of text, often adding sensory details or specific literary devices.
            *   **`Simile`:** Special handling to remove trailing punctuation from the input text and adds common simile starters like "like," "as if."
    *   **Extra Context and Memories (`extra_context`):**
        *   **How to Use:** Enter persistent information or "memories" for the AI here (e.g., "Your name is Sarah and you are a student at UBC"). This context is *always* included in the prompt.
        *   **What it Does:** Helps the AI maintain consistent character details, background information, or general knowledge throughout your session.
    *   **System Instruction (`context_replace`):**
        *   **How to Use:** If filled, this text *replaces* the AI's default "system instruction" from your loaded instruction template.
        *   **Use Case:** For highly specific scenarios where you need to fundamentally change the AI's role or core directive (e.g., "You are a grumpy old wizard who speaks only in riddles").
    *   **Instruction Prefix (`extra_prefix`):**
        *   **How to Use:** Text entered here is *always* inserted at the very beginning of your main instruction before it's sent to the AI (e.g., "Rewrite the following text: ").
        *   **Use Case:** Useful for tasks that consistently require an initial framing, like "Translate to French:", "Summarize:", etc.
        *   **`Rewrite` / `Clear` Buttons:** Quickly adds or removes the common "Rewrite the following text: " prefix.
    *   **Show Stats in divider (`add_stats`):**
        *   **How to Use:** Check this box.
        *   **What it Does:** When "Generate New" or "Gen with memory" is used, the divider (`~~~~`) will also include information about the model, active LoRA, temperature, top_p, top_k, and repetition penalty settings.
    *   **Help Tab:**
        *   **How to Use:** Click this tab.
        *   **What it Does:** Provides a built-in mini-guide explaining the core concepts and advanced features of Twinbook.

#### **B. Right Column: Your Work Area & Output**

This side is where the AI's generations appear and where you do your editing.

*   **Response Tab (`text_boxB`):**
    *   **How to Use:** This is your main working area. AI-generated text appears here. You can directly type, paste, select, and edit text within this box.
    *   **What it Does:** Displays the current state of your generated document. It also serves as the *context* for the AI's "Continue" operations.
    *   **The `~~~~` Separator:** When you use "Generate New" or "Gen with memory," the Twinbook extension inserts a `~~~~` (four tildes) separator. This visually demarcates independent AI generations. Critically, for "Continue" and "Gen with memory" operations, the AI *only considers the text that appears AFTER the last `~~~~` separator*. If you delete these separators or combine blocks, the AI's "memory" for continuation will change accordingly.
    *   **Selection Feature:** You can select a range of text within this box. This selection is used by "Continue [SEL]" and "Send [Sel] to Keep."
*   **Keep Tab (`text_boxC`):**
    *   **How to Use:** This acts as a temporary clipboard or scratchpad. You can copy selected text from the "Response" tab to here.
    *   **What it Does:** Stores text snippets you want to save or reference later, without them interfering with the AI's generation process.

---

### **3. Control Buttons**

These buttons drive the AI's generation and provide utility functions.

*   **Generate New (`generate_btn`):**
    *   **How to Use:** Click this button after entering an instruction in the "Instructions" box.
    *   **What it Does:** Triggers a fresh generation. A `~~~~` separator is inserted, and the AI starts writing *without* considering previous text in the "Response" box as context.
*   **Gen with memory (`generate_btnR`):**
    *   **How to Use:** Click this button after entering an instruction.
    *   **What it Does:** Similar to "Generate New" (it inserts a `~~~~` separator), but it sends the *last section* of the "Response" text (the part after the last `~~~~`) to the AI *as additional context or "memory"* before it generates its new response.
    *   **Use Case:** Useful for maintaining a thematic consistency or subtle influence from previous generations without a direct continuation.
*   **Continue (`continue_btn`):**
    *   **How to Use:** Click this button.
    *   **What it Does:** The AI will pick up from the *end of the last section* of text in the "Response" box (i.e., after the last `~~~~` separator) and continue writing, influenced by your current instruction.
*   **Continue [SEL] (`continue_btn_sel`):**
    *   **How to Use:** **Select a specific portion of text** in the "Response" box, then click this button.
    *   **What it Does:** The AI will use your *selected text* as the basis for its continuation, inserting the new generated text *immediately after your selection*. This is incredibly powerful for targeted expansions or edits within your document. Your instruction in the "Instructions" box will guide the continuation.
*   **Stop (`stop_btn`, `stop_btn2`):**
    *   **How to Use:** Click this button during an active generation.
    *   **What it Does:** Immediately halts the AI's generation process.
*   **Clear (`clear2`):**
    *   **How to Use:** Click this button.
    *   **What it Does:** Clears all text from the "Response" box. The previous content is saved to "Undo/Redo."
*   **Undo/Redo (`undo`):**
    *   **How to Use:** Click this button.
    *   **What it Does:** Toggles between the current content of the "Response" box and its state *before the last major change* (either a generation or a "Clear" action). It acts as a single-step undo/redo.
*   **[Sel] to Keep (`send_sel_keep`):**
    *   **How to Use:** **Select a specific portion of text** in the "Response" box, then click this button.
    *   **What it Does:** Appends your selected text to the content of the "Keep" tab, adding a `+++` separator for readability.

---

### **4. Persistence and Setup**

*   **Automatic Saving:** Twinbook automatically saves your last session's state (including the content of all textboxes and your settings for context, prefix, and stats) to a file named `last.json` in the extension's directory. This means your work is preserved across `text-generation-webui` restarts.
*   **Loading Last State:** When you open Twinbook, it will attempt to load your previous session, picking up exactly where you left off.

Twinbook is a robust tool for interactive text generation and editing, offering a high degree of control for creative writers, researchers, and anyone needing to fine-tune AI-generated content. Experiment with its different generation modes and editing features to find the workflow that best suits your needs!
