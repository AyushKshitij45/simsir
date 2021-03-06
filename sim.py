import pandas as pd
import sqlite3 
from scipy.integrate import odeint
import matplotlib.pyplot as plt

conn = sqlite3.connect('simulation.db')
c=conn.cursor()

def create_table():
    
    create=str('CREATE TABLE stufftoplot(Day,Suspected,Infected,Recovered)')
    c.execute(create)
        

def adjust_rate(contact_rate, day):
    if day > lockdown:
        contact_rate=(contactRate*person_in_contactd)
        return contact_rate
    else:
        return contact_rate

# The SIR model differential equations.
def deriv(state, t, N, beta, gamma):
    S, I, R = state
    
    beta = adjust_rate(beta, t)
    # Change in S population over time
    dSdt = -beta * S * I / N
    # Change in I population over time
    dIdt = beta * S * I / N - gamma * I
    # Change in R population over time
    dRdt = gamma * I

    return dSdt, dIdt, dRdt



contactRate=float(input("Enter the risk of infection (eg: 7%=0.07): ") or 0.07)
person_in_contactb=int(input("Enter number of people a person meets(before lockdown) : ")or 10)
person_in_contactd=int(input("Enter number of people a person meets(during lockdown) : ")or 2)
lockdown=int(input("Number of days after which lockdown begins : ")or 10)
population=int(input("Enter the total population : ") or 780000000)
infectedPop=int(input("Enter the total infected population(initially) : ") or 1)
death_rate=float(input("Enter the death rate(death per person) : ")or 0.02)
recovery= int(input("Enter the recovery rate(days) : ")or 14)


effective_contact_rate = contactRate * person_in_contactb
recovery_rate = 1/recovery

# We'll compute this for fun
print("R0 is", effective_contact_rate / recovery_rate)

# What's our start population look like?
# Everyone not infected or recovered is susceptible
total_pop =population
print(total_pop)
recovered = 0
infected = infectedPop
death = death_rate
susceptible = total_pop - infected - recovered

# A list of days, 0-366
days = range(1, 367)

# Use differential equations magic with our population
ret = odeint(deriv,
             [susceptible, infected, recovered],
             days,
             args=(total_pop, effective_contact_rate, recovery_rate))
S, I, R = ret.T



# Build a dataframe
df = pd.DataFrame({
    'suseptible': S,
    'infected': I,
    'recovered': 0.98*R,
    'dead': 0.02*R,
    'day': days
})

df.to_sql('stufftoplot', conn, if_exists='replace',index=False)
 
c.execute('SELECT * FROM stufftoplot')

for row in c.fetchall():
    print (row)

plt.style.use('ggplot')
df.plot(x='day',
        y=['infected', 'suseptible', 'recovered','dead'],
        color=['#bb6424', '#aac6ca', '#cc8ac0','#000000'],
        kind='area',
        stacked=False)


# As of Dec 31,2020 700000 people were infected and this model predicts 870000 
# which is off by just 170000 which means about 0.025%    