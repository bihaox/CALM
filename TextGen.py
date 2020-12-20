import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel, AutoTokenizer
import random
import torch.nn.functional as F
class TextGen:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("pranavpsv/gpt2-genre-story-generator")
        self.model = GPT2LMHeadModel.from_pretrained("pranavpsv/gpt2-genre-story-generator", return_dict=True)
        self.results = dict()
        self.total_loop = 0
    def get_next_logits(self,sentence):
        with torch.no_grad():
            inputs = self.tokenizer(sentence,add_special_tokens=True, padding=True)
            outputs = self.model(torch.tensor(inputs['input_ids']))
            loss = outputs.loss
            logits = outputs.logits[-1, :]
            return logits
    def get_prob_from_logits(self,idx, logits):
        prob = logits[idx]
        return prob
    def get_word_id_form_dict(self, word):
        return self.tokenizer.get_vocab().get('Ġ'+ word)
    

    
    def nucleus_top_p_filtering(self, logits, top_p=0.0, filter_value=-float('Inf')):
        """
        get code from: https://gist.github.com/thomwolf/1a5a29f6962089e871b94cbd09daf317 
        Filter a distribution of logits using top-k and/or nucleus (top-p) filtering
            Args:
                logits: logits distribution shape (vocabulary size)
                top_k >0: keep only top k tokens with highest probability (top-k filtering).
                top_p >0.0: keep the top tokens with cumulative probability >= top_p (nucleus filtering).
                    Nucleus filtering is described in Holtzman et al. (http://arxiv.org/abs/1904.09751)
        """
        assert logits.dim() == 1  # batch size 1 for now - could be updated for more but the code would be less clear
        
        if top_p > 0.0:
            sorted_logits, sorted_indices = torch.sort(logits, descending=True)
            cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)

            # Remove tokens with cumulative probability above the threshold
            sorted_indices_to_remove = cumulative_probs > top_p
            # Shift the indices to the right to keep also the first token above the threshold
            sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
            sorted_indices_to_remove[..., 0] = 0

            indices_to_remove = sorted_indices[sorted_indices_to_remove]
            logits[indices_to_remove] = filter_value
        return logits
    
    def random_generate(self, input_word, genre, total_loop):
        '''
        This function take input_word and genre gerate randomly with nucleus sample
        '''
        sent = '<BOS> <'+ genre +'>' + input_word 
        current_word = input_word
        for i in range(total_loop):
            logits = self.get_next_logits(sent)
            copy_logits = logits.clone().detach()

            filtered_logits = self.nucleus_top_p_filtering(copy_logits, top_p=0.9)
            probabilities = F.softmax(filtered_logits, dim=-1)
            next_id = torch.multinomial(probabilities, 1)

            next_word = self.tokenizer.decode(next_id)
            current_word += next_word 
            sent += next_word
            
        return current_word
        
    
    def get_nucleus_results(self, input_word, target_word, genre, search_size):
        '''
        This function will store nucleus results in a dict as a search space to further search 
        '''

        sent = '<BOS> <'+ genre +'>' + input_word
        current_word = input_word
        results = dict()
        for i in range(search_size):
            logits = self.get_next_logits(sent)
            copy_logits = logits.clone().detach()

            target_id = self.get_word_id_form_dict(target_word)
            if target_id == None:
                break
            target_prob = self.get_prob_from_logits(target_id, logits)

            filtered_logits = self.nucleus_top_p_filtering(copy_logits, top_p=0.9)
            probabilities = F.softmax(filtered_logits, dim=-1)
            next_id = torch.multinomial(probabilities, 1)
            next_word = self.tokenizer.decode(next_id)
            if (i == 0 and next_word[0]!=' '):
                _, topk_ids = torch.topk(logits, 10)
                next_id = topk_ids[random.randint(0,9)]
                next_word = self.tokenizer.decode([next_id])

            

            diff = self.get_prob_from_logits(next_id, logits) - target_prob
            temp_word = current_word + " " + target_word

            results[temp_word]= diff
             
            current_word += next_word
            sent += next_word
        return results

    def get_topk_results(self, input_word, target_word, genre, search_size):
        sent = '<BOS> <'+ genre +'>' + input_word
        current_word = input_word
        results = dict()
        for i in range(search_size):
            logits = self.get_next_logits(sent)


            target_id = self.get_word_id_form_dict(target_word)
            target_prob = self.get_prob_from_logits(target_id, logits)


            _, topk_ids = torch.topk(logits, 10)
            next_id = topk_ids[random.randint(0,9)]
            next_word = self.tokenizer.decode(next_id)
            while(target_word in target_list and next_word[0]!=' '):
                next_id = torch.multinomial(probabilities, 1)
                next_word = self.tokenizer.decode(next_id)

            diff = self.get_prob_from_logits(next_id, logits) - target_prob
            temp_word = current_word + " " + target_word
            results[temp_word]= diff
             
            current_word += next_word
            sent += next_word
        return results
    

    def generate_target_list(self, input_word, target_list, genre, total_loop, search_size, mode):
        current_word = input_word
        current_list = list(target_list)
        random.shuffle(current_list)
        length = len(target_list)
        for i in range(length):
            target_word = current_list.pop(0)
            random.shuffle(current_list)

            if mode == 'nucleus':
                results = self.get_nucleus_results(current_word, target_word, genre, search_size)
            elif mode == 'topk':
                results = self.get_topk_results(current_word, target_word, genre, search_size)

            min_diff = min(results.values())
            current_word = list(results.keys())[list(results.values()).index(min_diff)]
        result_word = self.random_generate(current_word,genre,total_loop)
        return result_word
            
            