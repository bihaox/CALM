import nltk
from collections import defaultdict
import random

class PosGen():
    
    def __init__(self):
        self.story_by_genre = defaultdict(list)
        with open('6_genre_clean_training_data.txt', 'r', errors ='replace') as ifp:
            for line in ifp.readlines():
                words = line.split()
                self.story_by_genre[words[1][1:-1]].append(' '.join(words[2:]))
                
    def generate(self, genre, target_word, TOTAL_LOOP, show_trace = False):
        index = random.randint(0, len(self.story_by_genre[genre])-1) #random.randint will sample the last index
        sent = self.story_by_genre[genre][index]
        pos_taggs = nltk.pos_tag(nltk.word_tokenize(sent))[:TOTAL_LOOP]
        
        print(pos_taggs)
        
        Done = False
        possible_indexes = []
        
        
        
        for i in range(len(pos_taggs)):
            if pos_taggs[i][1] in ('NN','NNS','NNP','NNPS') :
                Done = True
                possible_indexes.append(i)
                
        if Done == False:
            return 'generator failed to insert for this target word'
        
        
        if show_trace:
            pos_taggs[random.randint(0, len(possible_indexes)-1)] = ("""[[[""" +target_word+"""]]]""", pos_taggs[i][1])  
        else:
            pos_taggs[random.randint(0, len(possible_indexes)-1)] = (target_word, pos_taggs[i][1])
            
        modified_words = [i[0] for i in pos_taggs]
        
        return ' '.join(modified_words)
    
if __name__ == '__main__':
    posgen = PosGen()
    posgen.generate(genre='horror', target_word = 'pig', TOTAL_LOOP = 30,show_trace = True)