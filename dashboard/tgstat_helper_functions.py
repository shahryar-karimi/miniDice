from datetime import datetime, timedelta
import streamlit as st
import plotly.graph_objects as go
import pandas as pd


def plot_tgstat_channel_info(client, channel):
    """Display basic channel information from TGStat"""
    try:
        channel_info = client.get_channel_info(channel)
        
        if 'status' in channel_info and channel_info['status'] == 'ok' and 'response' in channel_info:
            response = channel_info['response']
            
            # Create two columns
            col1, col2 = st.columns(2)
            
            with col1:
                if 'avatar' in response:
                    st.image(response['avatar'], width=100)
                
                st.subheader(response.get('title', 'Channel Name Not Available'))
                st.write(f"@{response.get('username', channel)}")
                
                if 'description' in response:
                    st.write(response['description'])
            
            with col2:
                # Create metrics
                st.metric("Subscribers", response.get('participants_count', 'N/A'))
                
                if 'reach_daily' in response and 'reach' in response['reach_daily']:
                    st.metric("Daily Reach", response['reach_daily']['reach'])
                
                if 'er_daily' in response and 'er' in response['er_daily']:
                    st.metric("Engagement Rate", f"{response['er_daily']['er']}%")
                
                if 'tgstat_rating' in response and 'rating' in response['tgstat_rating']:
                    st.metric("TGStat Rating", response['tgstat_rating']['rating'])
        else:
            st.error(f"Error fetching channel info: {channel_info.get('error', 'Unknown error')}")
    except Exception as e:
        st.error(f"Error: {str(e)}")

def plot_tgstat_channel_stats(client, channel):
    """Display channel statistics from TGStat"""
    try:
        channel_stats = client.get_channel_stats(channel)
        
        if 'status' in channel_stats and channel_stats['status'] == 'ok' and 'response' in channel_stats:
            response = channel_stats['response']
            
            st.subheader("Channel Statistics")
            
            # Create metrics in multiple columns
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Posts Count", response.get('posts_count', 'N/A'))
                st.metric("Subscribers", response.get('participants_count', 'N/A'))
            
            with col2:
                st.metric("Average Post Reach", response.get('avg_post_reach', 'N/A'))
                st.metric("Average Posts Per Day", response.get('posts_per_day', 'N/A'))
            
            with col3:
                st.metric("Mentions Per Day", response.get('mentions_per_day', 'N/A'))
                st.metric("Forwards Per Day", response.get('forwards_per_day', 'N/A'))
        else:
            st.error(f"Error fetching channel stats: {channel_stats.get('error', 'Unknown error')}")
    except Exception as e:
        st.error(f"Error: {str(e)}")

def plot_tgstat_subscribers_growth(client, channel):
    """Display subscribers growth over time"""
    try:
        # Create group selector
        group_options = {
            "hour": "Hourly",
            "day": "Daily",
            "week": "Weekly", 
            "month": "Monthly"
        }
        
        # col1, col2 = st.columns([3, 1])
        # with col1:
        #     st.write(f"Fetching subscribers data for {channel}")
        # with col2:
        selected_group = st.selectbox(
            "Data grouping",
            options=list(group_options.keys()),
            format_func=lambda x: group_options[x],
            index=1  # Default to daily
        )
        
        # Get subscribers data with selected grouping, but without date constraints
        # to get whatever data is available
        start_date, end_date = st.slider(
            "Select date range",
            min_value=datetime(2025, 3, 10),
            max_value=datetime.today(),
            value=(datetime(2025, 3, 10), datetime.today()),
            step=timedelta(days=1)
        )
        start_date_timestamp = int(start_date.timestamp())
        end_date_timestamp = int(end_date.timestamp())
        
        subscribers_data = client.get_channel_subscribers(
            channel, 
            startDate=start_date_timestamp,
            endDate=end_date_timestamp,
            group=selected_group
        )
        
        if 'status' in subscribers_data and subscribers_data['status'] == 'ok' and 'response' in subscribers_data:
            response = subscribers_data['response']
            
            
            if response and len(response) > 0:
                st.subheader(f"Subscribers Growth - {group_options[selected_group]} View")
                
                # Prepare data for chart
                dates = []
                subscribers = []
                
                if isinstance(response, list):
                    # Log the raw data first for debugging
                    # st.write(f"Raw data: {len(response)} points received")
                    
                    # Sort by period to ensure chronological order
                    response.sort(key=lambda x: x.get('period', ''))
                    
                    for item in response:
                        if isinstance(item, dict):
                            # The API returns 'period' and 'participants_count'
                            date_val = item.get('period')
                            sub_val = item.get('participants_count')
                            
                            if date_val and sub_val:
                                dates.append(date_val)
                                subscribers.append(sub_val)
                                # st.write(f"Point: {date_val} - {sub_val} subscribers")
                
                st.write(f"Processed {len(dates)} valid data points")
                
                if len(dates) >= 1:
                    # If we have only one data point, we'll just show the current value
                    if len(dates) == 1:
                        st.info(f"Only one data point available: {dates[0]} with {subscribers[0]:,} subscribers")
                        
                        # Display single metric
                        st.metric("Current Subscribers", f"{subscribers[0]:,}")
                    else:
                        # Create Plotly figure
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=dates,
                            y=subscribers,
                            mode='lines+markers',
                            name='Subscribers'
                        ))
                        
                        fig.update_layout(
                            title=f"Subscribers Growth ({group_options[selected_group]})",
                            xaxis_title="Period",
                            yaxis_title="Subscribers",
                            template="plotly_dark",
                            height=500
                        )
                        
                        # Add hover information
                        fig.update_traces(
                            hovertemplate="<b>Period:</b> %{x}<br><b>Subscribers:</b> %{y:,}<extra></extra>"
                        )
                        
                        # Calculate and display the growth percentage
                        if len(subscribers) >= 2:
                            growth = subscribers[-1] - subscribers[0]
                            growth_percent = (growth / subscribers[0] * 100) if subscribers[0] > 0 else 0
                            
                            # Add metrics above the chart
                            cols = st.columns(3)
                            with cols[0]:
                                st.metric("Starting Subscribers", f"{subscribers[0]:,}")
                            with cols[1]:
                                st.metric("Current Subscribers", f"{subscribers[-1]:,}")
                            with cols[2]:
                                st.metric("Change", f"{growth:+,}", f"{growth_percent:.1f}%")
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Show subscriber changes over time
                        if len(subscribers) > 1:
                            changes = []
                            change_dates = []
                            
                            for i in range(1, len(subscribers)):
                                change = subscribers[i] - subscribers[i-1]
                                changes.append(change)
                                change_dates.append(dates[i])
                            
                            fig_changes = go.Figure()
                            fig_changes.add_trace(go.Bar(
                                x=change_dates,
                                y=changes,
                                marker_color=['green' if x >= 0 else 'red' for x in changes]
                            ))
                            
                            fig_changes.update_layout(
                                title=f"Subscriber Changes ({group_options[selected_group]})",
                                xaxis_title="Period",
                                yaxis_title="Change in Subscribers",
                                template="plotly_dark",
                                height=400
                            )
                            
                            fig_changes.update_traces(
                                hovertemplate="<b>Period:</b> %{x}<br><b>Change:</b> %{y:+,}<extra></extra>"
                            )
                            
                            st.plotly_chart(fig_changes, use_container_width=True)
                else:
                    st.warning("No valid data points found to plot the subscribers graph")
                    st.info("This may happen if the channel is too new or if there is an issue with the API.")
            else:
                st.warning("Empty response received from the API")
                st.info("The API might not have data for this channel. Try a different channel or time period.")
        else:
            error_msg = subscribers_data.get('error', 'Unknown error') if isinstance(subscribers_data, dict) else f"Unexpected response: {subscribers_data}"
            st.error(f"Error fetching subscribers data: {error_msg}")
            st.json(subscribers_data)
    except Exception as e:
        st.error(f"Error plotting subscribers growth: {str(e)}")
        import traceback
        st.error(traceback.format_exc())

def get_channel_posts_with_dates(client, channel, limit=50):
    """Get channel posts with their publication dates for selection"""
    try:
        st.write(f"Fetching posts for channel: {channel}")
        posts_data = client.get_channel_posts(channel, limit=limit)
        
        if 'status' in posts_data and posts_data['status'] == 'ok' and 'response' in posts_data:
            response = posts_data['response']
            
            # Check for different response formats
            if isinstance(response, dict) and 'items' in response:
                # If response is a dict with 'items' key containing the posts
                response = response['items']
                # st.write(f"Found posts in response['items']. Total items: {len(response)}")
            elif isinstance(response, dict):
                # Display the structure to debug
                # st.write("Response is a dictionary. Keys:", list(response.keys()))
                if 'posts' in response:
                    response = response['posts']
                    # st.write(f"Found posts in response['posts']. Total items: {len(response)}")
                else:
                    st.error("Couldn't find posts list in response")
                    st.json(response)
                    return []
            
            # st.write(f"Processing {len(response) if isinstance(response, list) else 'Not a list'} items")
            
            # Format posts data for selection
            posts_for_selection = []
            
            if not isinstance(response, list):
                st.error(f"Expected list response but got: {type(response)}")
                st.json(response)
                return []
                
            for post in response:
                # Skip if post is not a dictionary
                if not isinstance(post, dict):
                    st.write(f"Skipping non-dictionary post: {type(post)}")
                    continue
                    
                # Extract post ID and format date
                post_id = post.get('id')
                post_date = post.get('date', 'Unknown date')
                post_text = post.get('text', '')
                
                # Create summary of post content (limit to 50 chars)
                post_summary = post_text[:50] + "..." if len(post_text) > 50 else post_text
                
                # Add to selection list
                posts_for_selection.append({
                    'id': post_id,
                    'date': post_date,
                    'summary': post_summary,
                    'full_post': post
                })
            
            # st.write(f"Processed {len(posts_for_selection)} valid posts")
            return posts_for_selection
        else:
            error_msg = posts_data.get('error', 'Unknown error') if isinstance(posts_data, dict) else f"Unexpected response: {posts_data}"
            st.error(f"Error fetching posts: {error_msg}")
            st.json(posts_data)
            return []
    except Exception as e:
        st.error(f"Error: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return []

def compare_stats_between_posts(client, channel, start_post_id, end_post_id):
    """Compare channel statistics between two posts"""
    try:
        # Get post info for both posts to determine their dates
        start_post_info = client.get_post_info(start_post_id)
        end_post_info = client.get_post_info(end_post_id)
        
        if ('status' in start_post_info and start_post_info['status'] == 'ok' and 
            'status' in end_post_info and end_post_info['status'] == 'ok'):
            
            # Debug post info format
            st.write("Start post date type:", type(start_post_info['response']['date']))
            
            # Convert date to string if it's an integer (timestamp)
            if isinstance(start_post_info['response']['date'], int):
                start_post_date = datetime.fromtimestamp(start_post_info['response']['date'])
            else:
                start_post_date = datetime.strptime(start_post_info['response']['date'], '%Y-%m-%d %H:%M:%S')
                
            if isinstance(end_post_info['response']['date'], int):
                end_post_date = datetime.fromtimestamp(end_post_info['response']['date'])
            else:
                end_post_date = datetime.strptime(end_post_info['response']['date'], '%Y-%m-%d %H:%M:%S')
            
            # Make sure start date is before end date
            if start_post_date > end_post_date:
                start_post_date, end_post_date = end_post_date, start_post_date
                start_post_id, end_post_id = end_post_id, start_post_id
            
            # Display post information
            st.subheader("Selected Posts Period")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Starting Post**")
                st.write(f"Date: {start_post_date.strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"ID: {start_post_id}")
                if 'text' in start_post_info['response']:
                    post_text = start_post_info['response']['text']
                    if len(post_text) > 200:
                        post_text = post_text[:200] + "..."
                    st.markdown(post_text, unsafe_allow_html=True)
            
            with col2:
                st.write("**Ending Post**")
                st.write(f"Date: {end_post_date.strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"ID: {end_post_id}")
                if 'text' in end_post_info['response']:
                    post_text = end_post_info['response']['text']
                    if len(post_text) > 200:
                        post_text = post_text[:200] + "..."
                    st.markdown(post_text, unsafe_allow_html=True)
            
            # Format dates for API calls
            start_date_str = start_post_date.strftime('%Y-%m-%d')
            end_date_str = end_post_date.strftime('%Y-%m-%d')
            
            # Get subscribers data for this period
            subscribers_data = client.get_subscribers_graph(channel, start_post_date, end_post_date)
            
            # Display period statistics
            st.subheader(f"Statistics Between Posts ({(end_post_date - start_post_date).days} days)")
            
            # Calculate stats between the posts
            if ('status' in subscribers_data and subscribers_data['status'] == 'ok' and 
                'response' in subscribers_data and subscribers_data['response']):
                
                # Prepare data for charts
                dates = []
                subscribers = []
                daily_change = []
                
                response = subscribers_data['response']
                
                # Sort response by date to ensure proper order
                response.sort(key=lambda x: x.get('date'))
                
                for i, item in enumerate(response):
                    dates.append(item.get('date'))
                    current_subs = item.get('participants')
                    subscribers.append(current_subs)
                    
                    # Calculate daily change
                    if i > 0:
                        prev_subs = response[i-1].get('participants')
                        change = current_subs - prev_subs
                        daily_change.append(change)
                
                # Create metrics
                if len(subscribers) >= 2:
                    total_growth = subscribers[-1] - subscribers[0]
                    growth_percent = (total_growth / subscribers[0]) * 100 if subscribers[0] > 0 else 0
                    avg_daily_growth = sum(daily_change) / len(daily_change) if daily_change else 0
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Starting Subscribers", subscribers[0])
                        st.metric("Ending Subscribers", subscribers[-1])
                    
                    with col2:
                        st.metric("Total Growth", total_growth, f"{growth_percent:.2f}%")
                        st.metric("Average Daily Growth", f"{avg_daily_growth:.2f}")
                    
                    with col3:
                        # Calculate some additional metrics
                        max_daily_growth = max(daily_change) if daily_change else 0
                        min_daily_growth = min(daily_change) if daily_change else 0
                        
                        st.metric("Best Day Growth", max_daily_growth)
                        st.metric("Worst Day Growth", min_daily_growth)
                
                # Create Plotly figure for subscribers
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=subscribers,
                    mode='lines+markers',
                    name='Subscribers'
                ))
                
                fig.update_layout(
                    title="Subscribers Growth During Selected Period",
                    xaxis_title="Date",
                    yaxis_title="Subscribers",
                    template="plotly_dark"
                )
                
                st.plotly_chart(fig)
                
                # Create Plotly figure for daily change
                if daily_change:
                    fig_daily = go.Figure()
                    fig_daily.add_trace(go.Bar(
                        x=dates[1:],  # Skip first date as we don't have change for it
                        y=daily_change,
                        name='Daily Change'
                    ))
                    
                    fig_daily.update_layout(
                        title="Daily Subscribers Change",
                        xaxis_title="Date",
                        yaxis_title="Change",
                        template="plotly_dark"
                    )
                    
                    st.plotly_chart(fig_daily)
            else:
                st.warning("No subscribers data available for the selected period")
            
            # Get posts data for this period
            posts_data = client.search_posts(f"@{channel}", limit=50, 
                                           start_date=start_post_date, 
                                           end_date=end_post_date)
            
            if ('status' in posts_data and posts_data['status'] == 'ok' and 
                'response' in posts_data and 'items' in posts_data['response']):
                
                posts = posts_data['response']['items']
                
                # Display posts stats
                st.subheader(f"Posts During This Period ({len(posts)} posts)")
                
                if posts:
                    # Prepare data
                    post_dates = []
                    post_views = []
                    
                    for post in posts:
                        post_dates.append(post.get('date'))
                        post_views.append(post.get('views', 0))
                    
                    # Calculate metrics
                    avg_views = sum(post_views) / len(post_views) if post_views else 0
                    total_views = sum(post_views)
                    max_views = max(post_views) if post_views else 0
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Posts", len(posts))
                        st.metric("Posts Per Day", f"{len(posts) / (end_post_date - start_post_date).days:.2f}")
                    
                    with col2:
                        st.metric("Total Views", total_views)
                        st.metric("Average Views", f"{avg_views:.2f}")
                    
                    with col3:
                        st.metric("Max Views", max_views)
                        st.metric("Views Per Subscriber", f"{total_views / subscribers[-1]:.2f}" if subscribers else "N/A")
                    
                    # Create views chart
                    fig_views = go.Figure()
                    fig_views.add_trace(go.Bar(
                        x=post_dates,
                        y=post_views,
                        name='Post Views'
                    ))
                    
                    fig_views.update_layout(
                        title="Post Views During Selected Period",
                        xaxis_title="Date",
                        yaxis_title="Views",
                        template="plotly_dark"
                    )
                    
                    st.plotly_chart(fig_views)
                    
                    # Show table of posts
                    st.write("Posts List")
                    
                    posts_df = pd.DataFrame([{
                        'Date': post.get('date'),
                        'Views': post.get('views', 0),
                        'Text': post.get('text', '')[:100] + "..." if post.get('text', '') and len(post.get('text', '')) > 100 else post.get('text', '')
                    } for post in posts])
                    
                    st.dataframe(posts_df.sort_values('Date', ascending=False))
                    
                    # Display full text of first few posts
                    st.subheader("Latest Posts Content")
                    for post in posts[:5]:  # Show first 5 posts
                        st.write(f"**Date:** {post.get('date')}")
                        if post.get('views'):
                            st.write(f"**Views:** {post.get('views')}")
                        st.write("**Content:**")
                        st.markdown(post.get('text', ''), unsafe_allow_html=True)
                        st.markdown("---")
                else:
                    st.info("No posts found in the selected period")
            else:
                st.warning("Could not fetch posts data for the selected period")
        else:
            st.error("Error fetching post information")
    except Exception as e:
        st.error(f"Error comparing stats: {str(e)}")
