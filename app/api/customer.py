from flask import Flask, jsonify, json, request, abort, render_template, Blueprint, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.serializer import loads, dumps
from datetime import datetime
from . import customer_bp
from ..database import session_scope

from ..customer.service import CustomerService
from ..address.service import AddressService

@customer_bp.route('/customers/GetCustomerById/<id>', methods=['GET'])
def GetCustomerById(id):

    try:
        result = {}

        customer = CustomerService.getCustomerById(id)

        if customer:
            billing_address = AddressService.getCustomerBillingAddress(customer.cust_no)
            shipping_addresses = AddressService.getAllShippingAddressByCustNo(customer.cust_no)

            result['id'] = customer.id
            result['customerNo'] = customer.cust_no
            result['name'] = customer.name
            result['email'] = AddressService.getEmailByCustomerNo(customer.cust_no)
            result['status'] = customer.status
            result['modified'] = customer._modified
            result['address'] = AddressService.buildCustomerBillingAddress(billing_address)
            result['shippingAddresses'] = AddressService.buildCustomerShippingAddresses(shipping_addresses)

        return Response(status=200, mimetype='application/json', response= json.dumps(result) if result else 'null')
    except Exception as ex:
        abort(404, description=str(ex))


@customer_bp.route('/customers/GetRecentCustomers', methods=['GET'])
def GetRecentCustomers():
    try:
        result = []  

        lastSynchronized = request.args.get('lastSynchronized')
        
        if not lastSynchronized:
            raise Exception("missing lastSynchronized")
        
        modified = datetime.strptime(lastSynchronized, '%m/%d/%Y %H:%M:%S %p').strftime('%Y-%m-%d %H:%M:%S %p') 

        customers = CustomerService.getRecentCustomers(modified)

        for customer in customers:
                billing_address = AddressService.getCustomerBillingAddress(customer.cust_no)
                shipping_addresses = AddressService.getAllShippingAddressByCustNo(customer.cust_no)

                result.append({
                    'id': customer.id,
                    'customerNo': customer.cust_no,
                    'name': customer.name,
                    'email': AddressService.getEmailByCustomerNo(customer.cust_no),
                    'status': customer.status,
                    'modified': customer._modified,
                    'address': AddressService.buildCustomerBillingAddress(billing_address),
                    'shippingAddresses': AddressService.buildCustomerShippingAddresses(shipping_addresses)
                })

        return Response(status=200, mimetype='application/json', response= json.dumps(result) if result else 'null')

    except Exception as e:
        abort(404, description=str(e))

    return result