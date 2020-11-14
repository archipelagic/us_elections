# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 14:43:14 2020

@author: issind
"""

import pandas as pd
import requests as rq

class votes_methods:
        
    # Call the API
    def get_api_results():
        
        # All US States
        states = [
        'Alaska', 'Alabama', 'Arkansas', 'Arizona', 'California', 'Colorado',
        'Connecticut', 'Delaware', 'Florida', 'Georgia',
        'Hawaii', 'Iowa', 'Idaho', 'Illinois', 'Indiana', 'Kansas', 'Kentucky',
        'Louisiana', 'Massachusetts', 'Maryland', 'Maine', 'Michigan',
        'Minnesota', 'Missouri', 'Mississippi', 'Montana', 'North Carolina',
        'North Dakota', 'Nebraska', 'New Hampshire', 'New Jersey', 'New Mexico',
        'Nevada', 'New York', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania',
        'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas',
        'Utah', 'Virginia', 'Vermont', 'Washington', 'Wisconsin',
        'West Virginia', 'Wyoming',
        ]
    
        api_results = {}
         
        for state in states:
            formatted_state = state.lower().replace(' ', '-')
            state_results = rq.get('https://static01.nyt.com/elections-assets/2020/data/api/2020-11-03/race-page/{}/president.json'.format(formatted_state)).json()
            api_results[formatted_state] = state_results
            
        return api_results

    # Prepare the input for the data frame
    def format_input_for_df(api_results):
        records = []
        for state, state_results in api_results.items():
            race = state_results['data']['races'][0]
    
            for data_point in race['timeseries']:
                data_point['state']  = state
    
                # Get the share of the vote for a given batch
                data_point['vote_share_rep'] = data_point['vote_shares']['trumpd']
                data_point['vote_share_dem'] = data_point['vote_shares']['bidenj']
                two_party_share = data_point['vote_shares']['trumpd'] + data_point['vote_shares']['bidenj']
                if two_party_share > 0:
                    data_point['vote_share_trd'] = 1 - two_party_share
                else:
                    data_point['vote_share_trd'] = 0
    
                # Remove columns we don't need
                data_point.pop('vote_shares')
                data_point.pop('eevp_source')
    
                records.append(data_point)
                
        return records
    
    # To parse the original API data into a "base" data frame
    def format_df(records):
        
        df = pd.DataFrame.from_records(records)
        # Remove rows with NaN values
        df.dropna(inplace = True)
        # Transform 'object' column to proper datetime
        df.timestamp =  pd.to_datetime(df.timestamp)
        
        return df
    
    def get_final_votes_df(api_results):
        records = []
        for state, state_results in api_results.items():
            race = state_results['data']['races'][0]
    
            for candidate in race['candidates']:
                candidate['state']  = state
                records.append(candidate)
    
        return pd.DataFrame.from_records(records)
                
            
    
    # Get a separate, cleaned-up data frame for each state. 'state' is string
    def get_state_df_total(state, base_df):
    
        # Select only the specified state
        state_df = base_df.where(base_df.state == state)
        
        # Add column with batch size (difference of consecutive rows)
        state_df['batch_size'] = state_df.votes.diff()
        state_df.dropna(inplace = True)
        
        # Add column for ratio of dem/rep votes
        state_df['d_r_ratio'] = (state_df.vote_share_dem/state_df.vote_share_rep).round(3)
        
        # Rename columns to change table into long-form (for seaborn)
        state_df.rename(columns = {"vote_share_rep" : "rep", 'vote_share_dem' : 'dem', 'vote_share_trd' : 'trd'}, inplace = True)
        state_df = pd.melt(state_df, id_vars = ['votes','eevp','timestamp','state', 'batch_size', 'd_r_ratio'], var_name = 'party', value_name = 'vote_share')
        
        return state_df

    
    def get_state_df_batch(state, base_df):
        
        state_df = votes_methods.get_state_df_total(state, base_df)
    
        # Add columns counting all votes for a party
        state_df['num_votes'] = (state_df['votes']* state_df['vote_share']).round()
        
        # Add votes won since last timestamp
        state_df['delta_votes'] = state_df.groupby(['party'])['num_votes'].diff()
        
        # Replace occurences of NaN with num_votes (i.e. the number of votes in the first batch)
        state_df.loc[(state_df.delta_votes.isnull()),'delta_votes']=state_df.num_votes
        
        # Add batch percentage of votes
        state_df['batch_share'] = (state_df['delta_votes']/state_df['batch_size']).round(3)
    
        return state_df
    