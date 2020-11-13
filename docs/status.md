---
layout: default
title: Status
---

## Project Summary

We consider the problem of generating environment aware, style specific text snippets in Minecraft. Concretely, our agent will take as input 
the environment object string such as "dirt" and "diamond" retrieved from Minecraft and output style specific synthetic texts related to 
the input, such as horror stories and super hero stories. 


## Approach

We choose pretrained GPT-2 model fine tuned on style specific corpus such as horror story and super hero stories for language generation. The decoding algorithm is currently
implemented as modified top-k sampling to make sure the input word appears in the output text snippet. At each language generation step, the pretrained model ouputs a categorical distribution of corpus size that specifies the likelihood of the corresponding words to appear at the current position. Traditional, the word chosen at each generation step is achived by approaches such as nucleus sampling and top-k sampling([see here](https://arxiv.org/pdf/1904.09751.pdf)). 

To achieve context aware langauge generation, our system retrieves description of surrounding blocks from adjacent blocks of the agent(such as 'diamond_block') and returns a string that is common in natural language('diamond'). We then try to make the target word appear in our output text snippet. Formally, the context aware language generation task is defined as finding a sequence $$(w_1,w_2,w_3... w_n)$$ with an victim word $$w_v$$ such that $$p(target word|w_0, ... , w_{v-1})-p(w_v|w_0, ... , w_{v_1})$$ is minimized. 

![](src/decoding.png){:height="70%" width="70%"}

To find the optimal sequence, our system generates candidate sequence by computing the potential target word swapping loss $$p(target word|h)-p(chosen word|h)$$, and view the current sequence as a candidate hypothesis if such loss is smaller than a pre-defined threshhold. Upon generation of hypothesis, the word swapping loss is assigned to the sequence. Meanwhile, the system will keep checking the alternative possibility where the word swapp did not happen untill another hypothesis generation point is reached or limit of sentence length is reached.



## Evaluation

### Style coherent

To ensure the reults we generated are style coherent, we choose to use human evaluation metrics to ensure the ouputs are indeed of the intended style. Specifically, we randomly sample sentences with different styles from our system, and let human readers guess the genre of the generated sentence. 

### Syntactically sound

To ensure our method only impose minimal damage to the ability of language model to generate syntactically correct text, we use an open source grammar checker to check the suspected grammar errors in our generated text.

## Remaining Goals and Challenges

We plan to improve our system by both improving our generation algorithm and the ease-of-use of the system. In the following periods, we plan to change our current usage of top-k sampling to nucleus sampling to enhance the naturalness of our generated text. Meanwhile, the current system lacks the ability to deal with composite blocks in the environment, for example, the system cannot retrieve the word "tree" from the environment as trees are represented in Minecraft as the composition of wood blocks and leaf blocks. Finally, we plan to augment our language generation process by using existing ontologies such as wordnet to construct more candidate target words(for example, given pigs, hogs could also be a candidate word) to encourage more variants in our ouput.

## Resources Used

* [Hugging Face pretrained models](https://huggingface.co/)
* [NLTK](https://www.nltk.org/)
* [Grammar Checker in Python](https://pypi.org/project/grammar-check/)
