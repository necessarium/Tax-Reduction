def ask(prompt):
	while True:
		int_var = str(input(f"\t{prompt}"))
		try:
			float_var = float(int_var)
		except ValueError:
			count_delete = len(prompt + str(int_var)) + 6
			print("\033[A" + ' ' * count_delete + "\033[A")
			continue
		break
	return float_var


def find_standard_deduction():
    deduction_amount = {"Yes": 1100, "No": 12400}
    while True:
        question = "Can you be claimed as a dependent? "
        dependent_status = str(input(f"\t{question }"))
        try:
            key_format = dependent_status.replace(' ', '').title()
            standard_deduction = deduction_amount[key_format]
        except KeyError:
            count_delete = len(question + dependent_status) + 6
            print("\033[A" + ' ' * count_delete + "\033[A")
            continue
        break
    return standard_deduction


def find_tax_rate(long_capital_gains, short_capital_gains, total_deduction):
	total_taxable_income = long_capital_gains + short_capital_gains - total_deduction 

	if total_deduction > short_capital_gains:
		short_taxable_income = 0
		long_deduction = total_deduction - short_capital_gains 
		long_taxable_income = max(0, long_capital_gains - long_deduction)
	else:
		short_taxable_income = short_capital_gains - total_deduction 
		long_taxable_income = long_capital_gains

	#Start
	short_income_tax = 0

	#FEDERAL, short
	short_bracket_upper_bounds = [9950, 40525, 86375, 164925, 209425, 523600]
	short_bracket_upper_bounds.append(float('inf'))
	short_bracket_tax_rates = [0.1, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37]
	prev_bound = 0
	for i, bound in enumerate(short_bracket_upper_bounds):
		rate = short_bracket_tax_rates[i]
		bracket = bound - prev_bound
		if short_taxable_income > bound:
			short_income_tax += rate * bracket
			prev_bound = bound
		else:
			remainder = short_taxable_income - prev_bound
			short_income_tax += rate * remainder
			break
		
	#STATE, short
	short_bracket_upper_bounds = [1000, 2000, 3000, 100000, 125000, 150000, 250000]
	short_bracket_upper_bounds.append(float('inf'))
	short_bracket_tax_rates = [0.02, 0.03, 0.04, 0.0475, 0.05, 0.0525, 0.055, 0.0575]
	flat_bracket_fee = [0, 20, 50, 90, 4697.50, 5947.50, 7260, 12760]
	prev_bound = 0
	for i, bound in enumerate(short_bracket_upper_bounds):
		rate = short_bracket_tax_rates[i]
		bracket = bound - prev_bound
		if short_taxable_income > bound:
			short_income_tax += rate * bracket + flat_bracket_fee[i]
			prev_bound = bound
		else:
			remainder = short_taxable_income - prev_bound
			short_income_tax += rate * remainder + flat_bracket_fee[i]
			break

	#COUNTY, short
	montgomery_short_tax_rate = 0.032
	short_income_tax += short_taxable_income * montgomery_short_tax_rate

	#FEDERAL, long
	relevant_bound = 40000
	relevant_rate = 0.15
	if (short_taxable_income < relevant_bound
	and total_taxable_income > relevant_bound):
		long_within_bound = relevant_bound - short_taxable_income
		long_taxed_portion = long_taxable_income - long_within_bound
		long_income_tax = relevant_rate * long_taxed_portion
	elif (short_taxable_income < relevant_bound
	and total_taxable_income < relevant_bound):
		long_income_tax = 0
	elif short_taxable_income > relevant_bound:
		long_income_tax = relevant_rate * long_taxable_income

	#STATE, long
	maryland_long_tax_rate = 0.0575
	long_income_tax += long_taxable_income * maryland_long_tax_rate

	total_income_tax = short_income_tax + long_income_tax
	total_gross_income = long_capital_gains + short_capital_gains
	overall_tax_rate = total_income_tax / total_gross_income

	return overall_tax_rate


def format_money(num):
    if num == 0:
	    return f"${num}" 
    else:
        return f"{str(int(abs(num)/num)).replace('1', '')}${round(abs(num), 2)}"

def main():
    print("PERSONAL")
    initial_gross_short_gains = ask("Gross short-term capital gains in USD:  ")
    gross_long_gains = ask("Gross long-term capital gains in USD: ")
    initial_gross_income = gross_long_gains + initial_gross_short_gains

    standard_deduction = find_standard_deduction()
    initial_tax_rate = find_tax_rate(gross_long_gains, initial_gross_short_gains, standard_deduction)
    initial_taxes_owed = initial_gross_income * initial_tax_rate

    print("\nOPERATION")
    sm_deduction = ask("Standard mileage deduction in cents: ")
    cost_per_mile = ask("Cost per mile in cents: ")
    mile_count = ask("Total miles in timeframe: ")
    rental_income = ask("Rental income per month: ")
    loan_payement = ask("Loan payment per month: ")
    insurance_costs = ask("Insurance cost per month: ")
    months_timeframe = ask("Total timeframe in months: ")

    miles_cost = mile_count * cost_per_mile / 100
    periodic_expenses = loan_payement + insurance_costs
    total_operating_cost = miles_cost + periodic_expenses * months_timeframe
    total_rental_income = rental_income * months_timeframe
    net_income = total_rental_income - total_operating_cost

    mileage_deduction = mile_count * sm_deduction / 100
    final_deduction = standard_deduction + mileage_deduction

    final_gross_short_gains = initial_gross_short_gains + rental_income * months_timeframe
    final_gross_income = gross_long_gains + final_gross_short_gains

    reduced_tax_rate = find_tax_rate(gross_long_gains, final_gross_short_gains, final_deduction)
    reduced_taxes_owed = final_gross_income * reduced_tax_rate
    net_tax_rate_decrease = initial_tax_rate - reduced_tax_rate
    net_tax_savings = initial_taxes_owed - reduced_taxes_owed

    print(f"\n\nGross short-term capital gains in USD: {format_money(initial_gross_short_gains)} -> {format_money(final_gross_short_gains)}\nTotal additional gross income from rent: $0 -> {format_money(total_rental_income)}\nTotal additional operating expenses: $0 -> {format_money(total_operating_cost)}\nOperation Net income = {format_money(net_income)}")

    print(f"\nTotal tax rate on all income: {round(100 * initial_tax_rate, 2)}% -> {round(100 * reduced_tax_rate, 2)}%\nTotal taxes owed on all income: {format_money(initial_taxes_owed)} -> {format_money(reduced_taxes_owed)}\nNet effective tax rate decrease = {round(100 * net_tax_rate_decrease, 2)}%\nNet tax savings = {format_money(net_tax_savings)}")


    r = 0.50
    miles_to_fuk_taxes = 100 * (initial_gross_income - standard_deduction)/sm_deduction
    print(f"\nCar equity at end of timeframe: {format_money((1-r) * loan_payement * months_timeframe)}\nTotal miles to get taxes to $0: {round(miles_to_fuk_taxes)}")


main()