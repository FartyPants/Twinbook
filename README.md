# Twinbook

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/Q5Q5MOB4M)

It looks simple. It works simple. But this is an extraordinary way of combining Instruction Chat with Notebook. You get two huge text boxes! On the left, for typing INSTRUCTIONS; on the right, for RESPONSE.

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

GEN WITH MEMORY: This function takes the last Response (i.e., after last Squiggly line, just like CONTINUE), and inserts it at the top of the LLM instruction, before System or Instruction commands. This means that the LLM gets to see the last response, but only as a memory. So it generates a NEW response, not a continuation of the text (like CONTIUE does), but with a faint remote ideas of previous facts. 

TThis is great for writing a new scene with new instructions for example - LLM still remembers the previous text (up to last squigly line)

Ugh, I know, it sounds complicated when you try to describe like this. You need to figure out how it works. It makes sense. I pinky swear.
