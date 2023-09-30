# Twinbook

It looks simple. It works simple. But this is an extraordinary way of combining Instruction Chat with Notebook. You get two huge text boxes! On the left, for typing INSTRUCTIONS; on the right, for RESPONSE.

So what, huh? Big deal!

Here’s how it works. Type ‘What’s your name?’ into the Instructions box and click GENERATE NEW. That prints something like ‘My name is Assistant’ into the right Response box. Oh, but you can type into the Response box as well, just like in the Notebook. For instance, you might delete the period and type ’ and I really like ’. 

Then when you click CONTINUE, it goes on generating more text. Probably how it really likes to help users answering their questions.

So far so good. But hey! Did you realize you could have also changed the INSTRUCTIONS itself before you hit Continue! Let's say, ‘Describe how you enjoy your ice-cream.’ And then hit CONTINUE. 

Suddenly it talks about ice cream, It uses the previous response plus the new instruction to continue generating the text. 

This way you can modify responses, in the middle of the text - sort of steer the LLM towards your goal. It’s like a chat where you control both sides of the discussion.

Now every time you click GENERATE NEW, it inserts those little squiggly lines (separator) into the Response window before it starts writing. Then it comes up with a whole NEW bit of text following the Instruction that doesn’t depend on the previous Responses.

By deleting or inserting these squigglies, you can tell the CONTINUE routine exactly what text to take into account.

GEN WITH MEMORY: This function takes the last Response (i.e., after last Squiggly line), and inserts it at the top of the LLM instruction, before System or Instruction command. This means that the LLM gets to see the last response, but only as a memory. So it generates a NEW response, not a continuation of the text, but with a faint remote ideas of previous facts. (It also appends the text to the last Response without the sqiggly separator, so you can repeat the Gen with memory process over and over with more memories being piled up)

Ugh, I know, it sounds complicated when you try to describe like this. You need to figure out how it works. It makes sense. I pinky swear.
