# TGStat API Client Library

A comprehensive Python client library for the [TGStat API](https://api.tgstat.ru/docs/ru/start/intro.html), which provides analytics and statistics for Telegram channels.

## Features

- Full support for API Stat (channel and post statistics)
- Full support for API Search (publication search)
- Full support for API Callback (notifications)
- Database and usage information endpoints
- Comprehensive test suite
- Well-documented methods with type annotations

## Installation

You can install this library directly from the source:

```bash
# Clone the repository
git clone <repository-url>
cd <repository-name>

# Install dependencies
pip install requests
```

## Usage

Here's a quick example of how to use the TGStat API client:

```python
from dashboard.tgstat_client import TGStatClient

# Initialize the client with your API key
client = TGStatClient("your_api_key_here")

# Get information about a channel
channel_info = client.get_channel_info("channelname")
print(channel_info)

# Search for channels
channels = client.search_channels("keyword", limit=10)
print(channels)

# Get channel statistics
stats = client.get_channel_stats("channelname")
print(stats)

# Search for posts
posts = client.search_posts("keyword", limit=10)
print(posts)
```

## API Endpoints

### Channel Methods

The library provides comprehensive access to channel-related endpoints:

- `get_channel_info(channel)`: Get basic information about a channel
- `search_channels(q, limit, offset, country, language, category)`: Search for channels
- `get_channel_stats(channel)`: Get channel statistics
- `get_channel_posts(channel, limit, offset)`: Get channel posts
- `get_channel_mentions(channel, limit, offset)`: Get channel mentions
- `get_channel_forwards(channel, limit, offset)`: Get channel forwards
- `get_channel_subscribers(channel, period)`: Get channel subscribers
- `get_channel_avg_posts_reach(channel, period)`: Get channel's average post reach
- `get_channel_err(channel)`: Get channel error rate (views/subscribers ratio)
- `get_channel_views(channel, period)`: Get channel views
- `get_subscribers_graph(channel, start_date, end_date)`: Get subscribers graph data
- `get_views_graph(channel, start_date, end_date)`: Get views graph data

### Post Methods

Access post-related endpoints:

- `get_post_info(post_id)`: Get information about a specific post
- `get_post_stats(post_id)`: Get statistics for a specific post

### Search Methods

Search for content within the Telegram ecosystem:

- `search_posts(q, limit, offset, min_views, start_date, end_date, extended, media_type, exclude_forwards)`: Search for posts
- `get_mentions_by_period(q, start_date, end_date)`: Get mentions by period
- `get_mentions_by_channels(q, limit, offset, start_date, end_date)`: Get mentions by channels

### Callback Methods

Manage notifications for new content:

- `set_callback_url(callback_url)`: Set callback URL for notifications
- `get_callback_info()`: Get information about configured callback
- `subscribe_channel(channel)`: Subscribe to channel notifications
- `subscribe_word(word)`: Subscribe to keyword notifications
- `get_subscriptions_list()`: Get list of active subscriptions
- `unsubscribe(subscription_id)`: Unsubscribe from notifications

### Database Methods

Access metadata about the API:

- `get_categories()`: Get available channel categories
- `get_countries()`: Get available countries
- `get_languages()`: Get available languages

### Usage Methods

Monitor your API usage:

- `get_usage_stat()`: Get usage statistics for your API token

## Running Tests

The library includes a comprehensive test suite. To run the tests:

```bash
python -m unittest dashboard.test_tgstat
```

## License

[Specify your license here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 