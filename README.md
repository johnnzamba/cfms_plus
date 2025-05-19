## Cfms Plus

An ENhanced Church Finance and ERP System

## Installation

For starters, ensure that [Frappe](https://github.com/frappe) is installed, since the application is built on FRAPPE FRAMEWORK. Additionally, ensure that [ERPNext](https://github.com/frappe/erpnext) is installed for concise accounting.


```bash
git clone https://github.com/johnnzamba/cfms_plus.git
```
```bash
cd cfms_plus
```

Now Since the App is already cloned, install it on your site:

```bash
bench -- {{site_name}} install-app cfms_plus
```

Finally do bench migrate to ensure the customizations and hooks are PROPERLY effected.

```bash
bench -- {{site_name}} migrate
```

Once this runs correctly, we are good to go! Utilize Workspace for in-app functionality; as shown below.


<br>
<a href="https://64.media.tumblr.com/5db39619ee090288e1349e9cf96b94b0/3ec77f73cb705a5d-27/s540x810/f626f6e6aafaa7b9acb73011c9cd2a083d727d52.pnj"><img src="https://64.media.tumblr.com/5db39619ee090288e1349e9cf96b94b0/3ec77f73cb705a5d-27/s540x810/f626f6e6aafaa7b9acb73011c9cd2a083d727d52.pnj"/></a>

<br>

## Acknowledgement

I want to acknowledge that this project is solely owned by me. All rights, including intellectual property rights, are retained by the original owner. The code, design, and any associated content are proprietary. For any inquiries, Please contact me [here](mailto:#{nzambakitheka@gmail.com}).

Thank you for your understanding and respect for the intellectual property rights associated with this project.

## License

Unless attributed otherwise, everything is under the MIT License (see LICENSE for more info).
