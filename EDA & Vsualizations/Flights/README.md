# Data Analysis of Ford GoBike - San Francisco Bay Area

## by Ananthalakshmi Dasaprakash


## Dataset

> This data set includes information about individual rides made in a bike-sharing system covering the greater San Francisco Bay area for the month of February 2019. Following is the data description of this dataset:
* duration_sec: Duration of the ride in seconds
* start_time: Start time of the ride
* end_time: End time of the ride
* start_station_id: Id of starting station
* start_station_name: Name of the starting station
* start_station_latitude: Latitude of starting station
* start_station_longitude: Longitude of starting station
* end_station_id: Id of end station
* end_station_name: Name of the end station
* end_station_latitude: Latitude of end station
* end_station_longitude: Longitude of end station
* bike_id: Id of the bike used for ride sharing
* user_type: Type of the user (Customer/Subscriber)
* member_birth_year: Birth year of the member or subscriber
* member_gender: Gender of the member or subscriber
* bike_share_for_all_trip: Boolean field which says if the bike is shared for the whole trip

## Summary of Findings

> * The data provided for analysis if the ride share data for February 2019
> * The frequency of rides were more for subscribers than customers. 89% of the rides are by subscibers and 11% by customers
> * Bike is shared for the whole trip only for 9% of the rides
> * Maximum number of rides happened on Thursdays and lowest on Saturday and Sunday compared to weekdays
> * Maximum number of rides were on 28th Feb and minimum on 9th Feb
> * Maximum number of rides were between 8-10AM and 5-7PM which are clearly peak hours
> * Market St at 10th St is where most rides originated
> * San Francisco Caltrain Station 2 had most rides in destination. Also, almost all stations in starting stations occurred on destination list too
> * 16th Street depot had the lowest rides for starting station and Willow St at Vine St has the lowest number of rides
> * 75% were male, 23% female and 2% Others based on gender data present
> * Even though the frequency of duration by user type is higher for subscriber the average duration travelled by customers (~ 1400) is higher than the customers (~ 600).
> * Even though the frequency of rides is lesser during the weekends, we observe the rides were of longer duration during weekends than during weekdays.
> * 17th February 2019 had the maximum duration of rides even though 28th Feb had the maximum frequency of rides
> * We can observe that peak hours doesn't contribute to the duration rather the highest duration happens at 3AM and next highest at 2AM.
> * Pattern of travel time observed during 2AM and 3AM where we expect rides to be longer during peak hours due to traffic


## Key Insights for Presentation

> * Subscriber vs Customer distribution
> * The busiest stations where most people onboarded
> * Behaviour of customers and subscribers during weekdays and weekends vs the frequency of rides
> * Behaviour of subscribers and customers during hours of the day vs the frequency of rides
> * Pattern of travel time observed during 2AM and 3AM where we expect rides to be longer during peak hours due to traffic