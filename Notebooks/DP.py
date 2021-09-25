import pickle
from matplotlib.pyplot import step
import streamlit as st
import pandas as pd
 
# loading the trained model
with open('./models/ski_resort_pricing_model.pkl', 'rb') as pickle_in:
    model = pickle.load(pickle_in)

ski_data = pd.read_csv('./data/ski_data_step3_features.csv')


@st.cache()
# defining the function which will make the prediction using the data which the user inputs 
def prediction(**kwargs):   
    print(kwargs.items())
#Refit model
    X = ski_data.loc[ski_data.Name != "Big Mountain Resort", model.X_columns]
    y = ski_data.loc[ski_data.Name != "Big Mountain Resort", 'AdultWeekend']
    model.fit(X, y)

    X_bm = ski_data.loc[ski_data.Name == "Big Mountain Resort", model.X_columns]
    y_bm = ski_data.loc[ski_data.Name == "Big Mountain Resort", 'AdultWeekend']
    y_bm = y_bm.values.item()
    bm_pred = model.predict(X_bm).item()

#Assign Features
    all_feats = ['vertical_drop', 'total_chairs', 'fastQuads', 'Runs', 'LongestRun_mi', 'trams', 'SkiableTerrain_ac']
    f={col:kwargs[col] for col in all_feats if col in kwargs.keys()}
    if 'snow_making' in kwargs.keys(): f['Snow Making_ac']=kwargs['snow_making']


# Making predictions 
    def predict_increase(features, deltas):
        bm2 = X_bm.copy()
        for f, d in zip(features, deltas):
            bm2[f] += d
        return model.predict(bm2).item() - model.predict(X_bm).item()

    return predict_increase(f.keys(), f.values())

      
  
# this is the main function in which we define our webpage  
def main():       
    # front end elements of the web page 
    html_temp = """ 
    <div style ="background-color:yellow;padding:13px"> 
    <h1 style ="color:black;text-align:center;">Big Mountain <br> Ticket Price Prediction</h1> 
    </div> 
    """
      
    # display the front end aspect
    st.markdown(html_temp, unsafe_allow_html = True) 

    #select parameters and select value
    selected_para1 = st.sidebar.multiselect(label='Prefered Parameters', options=sorted(['vertical_drop', 'Runs', 'fastQuads', 'Snow Making_ac']), default='vertical_drop')
    selected_para2 = st.sidebar.multiselect(label='Secondary Parameters', options=sorted(['total_chairs', 'LongestRun_mi', 'trams', 'SkiableTerrain_ac']), default='LongestRun_mi')
      
    # following lines create boxes in which user can enter data required to make prediction 
    s={}
    for p in selected_para1+selected_para2:
        if p in ["Runs","fastQuads","total_chairs","trams"]:
            current= st.number_input(p, step=1); result =""
        else:
            current= st.number_input(p); result =""
        if p != "Snow Making_ac":
            #s+= p+'=input_'+p+', '
            exec('input_'+p+' = current')
            exec('s[\''+p+'\']=input_'+p)

        else:
            #s+= 'snow_making=input_snow_making, '
            input_snow_making=current
            s['snow_making']=input_snow_making
        

    # when 'Predict' is clicked, make the prediction and store it 
    if st.button("Predict"): 
        result = prediction(**s)
        st.success('Your price for each ticket increased ${}.'.format(round(result,4)))
     
if __name__=='__main__': 
    main()