locust -f tests/locustfile.py --host=http://localhost:8000

## Example :

{
  "transac_type": "CASH_OUT",
  "amount": 181.00,
  "src_bal": 181.0	,
  "src_new_bal": 0,
  "dst_bal": 21182.0,
  "dst_new_bal": 0
}

## To-do

* Validation in Rest API
* Model path fixes
* Instruction to install more than docker