import json
from teamproject.crawler import get_data
from teamproject.models import BaselineAlgo
from teamproject.models import PoissonRegression
import pandas as pd



def outcome2int(match) -> int:
	if match.homeScore == match.guestScore:
		return 1
	elif match.homeScore > match.guestScore:
		return 0
	else:
		return 2

def prediction2int(pred:list) -> int:
	return pred.index(max(pred))


train_data = get_data(2015, 1, 2015, 100)
test_data = get_data(2016, 1, 2016, 10)

print(len(train_data))
print(len(test_data))

#train_data = get_data(2017, 1, 2017, 100)
#test_data = get_data(2019, 1, 2019, 10)



model_poisson = PoissonRegression(train_data)
model_baseline = BaselineAlgo(train_data)
print(model_baseline.predict("a", "b"))


model = model_poisson


num_correct = 0
num_incorrect = 0
num_total = len(test_data)

for index, row in test_data.iterrows():
    #outcome2int(row)

    prediction = model.predict(row.homeClub, row.guestClub)

    if outcome2int(row) == prediction2int(prediction):
    	num_correct += 1
    else:
    	num_incorrect +=1

    

#basline: 0.426, 0.573
#poisson: 0.423, 0.576


print(num_correct/num_total)
print(num_incorrect/num_total)