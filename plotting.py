# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 15:22:50 2020

@author: issind
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import seaborn as sns
from methods import votes_methods as vm


class plot_vote_graphs:
    
    sns.set_theme()
    
    # Plot percentage of votes per per and ratio of D/R votes. state param is string
    def plot_percentage(state_name, base_df, minus_days = 0, minus_hours = 0):
        
        state_df = vm.get_state_df_total(state_name, base_df)
        
        fig, (ax1, ax2) = plt.subplots(nrows = 2, figsize = (10,10), sharex = True)
        
        sns.set_style('darkgrid')
        sns.scatterplot(data = state_df, x = 'timestamp', y = 'vote_share', hue = 'party', palette=['red', 'blue', 'green'], markers=['o','+','x'], ax = ax1)
        sns.scatterplot(data = state_df, x = 'timestamp', y = 'd_r_ratio', palette = ['black'], ax = ax2)
    
        
        # Set title and labels for axes
        ax2.set(xlabel="Date",
                ylabel = "D/R votes Ratio",
                title = "Ratio of Democrat vs. Republican votes over time")
        ax1.set(ylabel="Percentage of votes",
               title="Share of votes per party over time")
    
        # round to nearest dates.
        datemin = np.datetime64(min(state_df.timestamp),'D')
        datemax = np.datetime64(max(state_df.timestamp),'D') - np.timedelta64(minus_days, 'D') - np.timedelta64(minus_hours, 'h')
        ax2.set_xlim(datemin, datemax)
    
        # Define the date format
        date_form = mdates.DateFormatter("%m-%d %H")
        ax2.xaxis_date()
        ax2.xaxis.set_major_formatter(date_form)

    # Plot the number of votes per party. state_name is a string
    def plot_total(state_name, base_df, minus_days = 0, minus_hours = 0):
        
        # Prepare the DF using the functions from methods.py
        state_df = vm.get_state_df_batch(state_name, base_df)
        
        fig, ax = plt.subplots(figsize = (10,10))
        
        sns.lineplot(data = state_df, x = 'timestamp', y = 'num_votes', hue  = 'party', palette=['red', 'blue', 'green'])
        
        # Set title and labels for axes
        ax.set(xlabel="Date",
               ylabel="Cumulative votes",
               title="Total votes by party over time")
        ax.legend()
        
        # round to nearest dates.
        datemin = np.datetime64(min(state_df.timestamp),'D')
        datemax = np.datetime64(max(state_df.timestamp),'D') - np.timedelta64(minus_days, 'D') - np.timedelta64(minus_hours, 'h')
        ax.set_xlim(datemin, datemax)
        
        # Define the date format
        date_form = mdates.DateFormatter("%m-%d %H")
        ax.xaxis_date()
        ax.xaxis.set_major_formatter(date_form)
        
    # Plot percentage of votes per per and ratio of D/R votes. state param is string
    def plot_batch_percentage(state_name, base_df, minus_days = 0, minus_hours = 0):
        
        # Prepare the DF using the functions from methods.py
        state_df = vm.get_state_df_batch(state_name, base_df)
        
        fig, (ax1, ax2) = plt.subplots(nrows = 2, figsize = (10,10), sharex = True)
        
        sns.set_style('darkgrid')
        sns.scatterplot(data = state_df, x = 'timestamp', y = 'batch_share', hue = 'party', palette=['red', 'blue', 'green'], markers=['o','+','x'], ax = ax1)
        sns.scatterplot(data = state_df, x = 'timestamp', y = 'delta_votes', hue = 'party', palette=['red', 'blue', 'green'], markers=['o','+','x'], ax = ax2)
        
        # Set title and labels for axes
        ax2.set(xlabel="Date",
                ylabel = "Total votes per batch",
                title = "Votes per batch by candidate")
        ax1.set(ylabel = "Percentage of votes in batch",
                title = "Batch percentages of votes by candidate")
    
        # round to nearest dates.
        datemin = np.datetime64(min(state_df.timestamp),'D')
        datemax = np.datetime64(max(state_df.timestamp),'D') - np.timedelta64(minus_days, 'D') - np.timedelta64(minus_hours, 'h')
        ax1.set_xlim(datemin, datemax)
        ax1.set_ylim(0,1)
        ax2.set_ylim(0)
    
        # Define the date format
        date_form = mdates.DateFormatter("%m-%d %H")
        ax1.xaxis_date()
        ax1.xaxis.set_major_formatter(date_form)
        
    
    def plot_absentee_percentage(api_results, list_of_states = []):
        
        # Get df with final results and keep only info for major parties
        final_votes = vm.get_final_votes_df(api_results)
        
        # Select only desired states, if a list is specified as an input
        if len(list_of_states) > 0:
            final_votes = final_votes[final_votes.state.isin(list_of_states)]
            
        #keep only Rep and Dem results
        final_votes =  final_votes[(final_votes.party_id == 'republican') | (final_votes.party_id == 'democrat')]
        
        fig, (ax1, ax2) = plt.subplots(nrows = 2, figsize = (20,20), sharex = True, sharey = True)
        
        plot1 = sns.barplot(data = final_votes, x = 'state', y = 'percent', hue = 'party_id', palette=['red', 'blue'], ax = ax1)
        plot2 = sns.barplot(data = final_votes, x = 'state', y = 'absentee_percent', hue = 'party_id', palette=['red', 'blue'], ax = ax2)
        
        for plot in (plot1, plot2):
            for item in plot.get_xticklabels():
                item.set_rotation(45)
        
        # Set title and labels for axes
        ax2.set(xlabel='', ylabel = "Percentage of votes", title = "Absentee ballots")
        ax1.set(title = "Total votes", ylabel ="Percentage of votes", xlabel = '')
        
        
        