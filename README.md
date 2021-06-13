# bofa

Stats program for valorant. Powered by python and selenium, scraped from vlr.

## Intro

This program aims to gather and manipulate relevant statistics about competitive valorant from VLR.gg

## Current capability

1. Takes data from a list of teams all the teams in an event and gathers statistics from all of their matches including separation by map

1. Supports filtering matches by event

1. Stores match data in an accessible python dict  

1. Records econ data form rounds such as half buys or full buys

1. Records agent selection (including player)

1. Records map and round data such as winner, loser, and round win type

## Planned capability

Currently this program gathers lots of data but does nothing besides print it to the console. There are plans to add functions for parsing this data into relevant statistics and information. If you understand python dicts you can easily pull query this information by accessing it in the statsDictOutputList dcit.

Additionally, these features are planned:

1. Filtering by date ranges

1. Accurate data on econ win calculations (low buy vs half buy, etc)

1. Filter all data for maps

1. Output to an accessible file format  

## Known issues

1. Missing pages - games missing data on VLR.gg for performance or econ can cause runtime errors. This will be addressed ASAP, but for now it is recommended to only look at teams where data is entered. Performance stats are commented out until a fix is implemented but you can uncomment it if you know what you're looking for

1. Possible issues with tournament formats that involve tying 

## Setup

This currently requires knowledge of programming to operate. That may change in the future.

Clone this repo. Download the [chrome web driver](https://chromedriver.chromium.org/downloads) and place it in the same directory as the .py files. I use Visual Studio, but I'm sure you can get this to work in your normal python environment. 
