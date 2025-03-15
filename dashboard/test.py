from TGstat import TGstat

apikey = 'e219a59c45d984685276cdd9f077eb74'
channel_id = 'dicemaniacs'

client = TGstat(apikey, channel_id)
stats = client.get_channel_statistics()
print(stats)