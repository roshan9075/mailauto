from django.shortcuts import render

from email.message import EmailMessage
from email.headerregistry import Address
from email.utils import make_msgid
import csv
import smtplib
import ssl
import  re
import dns
import dns.resolver
import socket
from django.template import RequestContext





# Create your views here.
def home(request):
	
	reciall=list()
	recicrt=list()
	failed=list()

	if request.method == "POST":
		sender_email = request.POST['i11']
		sender_pass = request.POST['i12']
		subject = request.POST['subject']
		body = request.POST['body']			

		f = request.FILES["contact_file"]
		with open('VM_MAIL/' + f.name, 'wb+') as destination:
			for chunk in f.chunks():
				destination.write(chunk)
		
		family =[]
		with open('VM_MAIL/' + f.name, 'r') as file:
			reader = csv.reader(file, delimiter="\n")
			family =[]
			for rows in reader:
				family.append(rows[0])
		print(family)

		
		for email_address in family:
			#Check using Regex
			addressToVerify = email_address
			addres_cpy=email_address
			match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', addressToVerify)

			if match == None:
	    		#print('Bad Syntax in ' + addressToVerify)
	    		#raise ValueError('Bad Syntax')
	    			failed.append(addressToVerify)
	    			continue

			# MX record
			#Pull domain name 
			domain_name = email_address.split('@')[1]
			#print(domain_name)

			#get the MX record for the domain
			#basically using gmail.com and getting Mx records
			records = dns.resolver.resolve(domain_name, 'MX')
			mxRecord = records[0].exchange
			mxRecord = str(mxRecord)


			# if the email address exists

			#local server hostname in which python is running
			host = socket.gethostname()

			# SMTP lib setup
			server = smtplib.SMTP()
			server.set_debuglevel(0)

			# SMTP Conversation
			server.connect(mxRecord)
			server.helo(host)
			server.mail('me@domain.com')#keep this as it is
			code, message = server.rcpt(str(addressToVerify))
			server.quit()

			# Assume 250 as Success
			if code == 250:
		    		#print('Y')
		    		recicrt.append(addres_cpy)
			else:
		    		#print('N')
		    		failed.append(addres_cpy)



		print(recicrt)
		print(failed)

		server1=smtplib.SMTP('smtp.gmail.com', 587)
		server1.starttls()
		server1.login(sender_email, sender_pass)

		mymsg = EmailMessage()
		mymsg['From'] = sender_email
		mymsg['To'] = ", ".join(recicrt)
		mymsg['Subject'] = subject
		mymsg.set_content(body, subtype = 'html')
		#asparagus_cid = make_msgid()
		server1.send_message(mymsg)

	return render(request, 'test.html', {"list":failed})
