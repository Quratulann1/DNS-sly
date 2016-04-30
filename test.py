from selenium import webdriver
import shlex
import sys
import subprocess
import pandas as pd
import time
import dns.resolver
from selenium.common.exceptions import TimeoutException

def usermapping(filename):
	ip_list=[]
	dict={}
	fopen=open(filename,"r")
	for line in fopen:
		col=line.split()
		if len(col) > 2 and col[2][0] != "/" and col[2] != "none" :
			ip_list.append(col[1])
			if col[1] in dict:
				dict[col[1]].append(col[2])
			else:
				dict[col[1]]=[col[2]]

	ip_set=set(ip_list)
	ip_list=[]
	for i in range(0,len(ip_set)):
		ip=ip_set.pop()
		ip_list.append(ip)

	domain_list=[]
	for ip in ip_list:
		domain_list.append(dict[ip])

	for i in range(0, len(domain_list)):
		domain_set=set(domain_list[i])
		print "*******user**********", ip_list[i]
		print "******domain_set*****", domain_set
		j=0 
		count=len(domain_set)
		fname=ip_list[i] + "_trace.txt"
		fout=open(fname,'w')
		while j < count:
			dom=domain_set.pop()
			num=domain_list[i].count(dom)
			output=dom+" "+str(num)
			fout.write(output)
			fout.write("\n")
			j=j+1

	print len(dict)
	


def collector(filename,user_name):
	trace_user=open(filename,'r')
	name_logfile="log_" + user_name + ".txt"
	fopen=open(name_logfile, "w")
	for line in trace_user:
		col=line.split()
		if len(col[0]) > 5 and col[0][4] == ":":
			url=col[0]
		else:
			url="http://" + col[0]

		try:
			answers = dns.resolver.query(col[0], 'A')
		except dns.exception.Timeout:
			# Bad things
			print "Error: dns.exception.Timeout"
			continue
		except dns.resolver.NoAnswer:
			print "Error: dns.resolver.NoAnswer"
			continue
		except dns.resolver.NoNameservers:
			print "Error: dns.resolver.NoNameservers "
			continue
		except dns.resolver.NXDOMAIN:
			print "dns.resolver.NXDOMAIN"
			continue
		except dns.name.LabelTooLong:
			print "dns.name.LabelTooLong"
			continue
		except dns.name.BadEscape:
			print "dns.name.BadEscape"
			continue
		except dns.name.EmptyLabel:
			print "dns.name.EmptyLabel"
			continue
		except dns.name.NeedAbsoluteNameOrOrigin:
			print "name.NeedAbsoluteNameOrOrigin"
			continue
		except dns.name.NameTooLong:
			print "Error: NameTooLong"
			continue
		except TimeoutException:
			print "Error: page took too long to load"
			continue
		else:
			command_string = "tcpdump -w myPackets.cap -vvv -l 'port 53'"
			tcpdumpProcess = subprocess.Popen(shlex.split(command_string), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

			driver=webdriver.Firefox()
			driver.get(url)
			# Let JS finish
			time.sleep(3)

			driver.close()
			tcpdumpProcess.terminate()
			tcpdump_stderr=tcpdumpProcess.communicate()
			tcpdumpProcess2 = subprocess.Popen(['tcpdump','-r', 'myPackets.cap'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			tcpdump_out, tcpdump_err = tcpdumpProcess2.communicate()
			fopen.write(tcpdump_out)

			print tcpdump_stderr
			print tcpdump_err

def main():

	usermapping("requests.dat") #output users and the domains they asked for ---- training period
	fin = open('10_plus_dns.csv','r')
	#fout=open("user_ip.txt","w")

	#getting users with more than 10 unique domains
	#uniq_users=[]
	#for line in fin:
	#	col=line.split()
	#	uniq_users.append(col[0])
	#set_uniqusers=set(uniq_users)
	#uniq_users=[]
	#for i in range(0,len(set_uniqusers)):
	#	ip=set_uniqusers.pop()
	#	fout.write(ip)
	#	fout.write("\n")
	#fout.close()
	#fin.close()
	#done

	fopen=open("user_ip.txt","r")
	for line in fopen:
		col=line.split()
		print col
		fname=col[0] + "_trace.txt"
		collector(fname,col[0])
	fopen.close()


if __name__ == "__main__":
    main()

