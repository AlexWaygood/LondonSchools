import pandas as pd
import numpy as np
from typing import NamedTuple

FILE_PATH = r'C:\Users\Alex\Google Drive\Exams final project_ evidence folder\Secondary school FOI data\Secondary school assessment policies v 27-05-21 csv.csv'


def GetFile() -> pd.DataFrame:
	return pd.read_csv(FILE_PATH)


class AnalysedData(NamedTuple):
	schools_who_responded: pd.DataFrame
	SchoolsWithAppeals: pd.DataFrame
	NumberWhoResponded: int
	NumberWhereAppealsAreApplicable: int
	NumberWithIncreaseInAppeals: int
	NumberWithDecreaseInAppeals: int
	AveragePercentageChangeInAppeals: float  # Expressed as a decimal
	AverageRawChangeInAppeals: float


def SchoolsWhoResponded(df: pd.DataFrame) -> AnalysedData:
	"""
	Filter out the schools who either didn't respond or are a special school.
	Get back a NamedTuple with a database of the remaining schools, a row count of that DataFrame, and some statistics on the data
	"""

	schools_who_responded = df.loc[(df['Response received?'] == 1) & (df['Response refused?'] != 0) & (df['Special school?'] != 1)]
	NumberWhoResponded = len(schools_who_responded.index)

	AppealsColumns = (
		'7biii). A level appeals: 2019-20',
		'7aiii). GCSE appeals: 2019-20',
		'7bii). A level appeals: 2018-19',
		'7aii). GCSE appeals: 2018-19'
	)

	schools_who_responded = schools_who_responded.fillna(0)

	SchoolsWithAppeals = schools_who_responded.loc[
		(schools_who_responded['7biii). A level appeals: 2019-20'] != -1)
		| (schools_who_responded['7aiii). GCSE appeals: 2019-20'] != -1)
	]

	NumberWhereAppealsAreApplicable = len(SchoolsWithAppeals.index)

	for col in AppealsColumns:
		SchoolsWithAppeals[col] = SchoolsWithAppeals[col].apply(lambda x : x if x > 0 else 0)

	SchoolsWithAppeals['Raw change in appeals 2019-2020'] = (
		(SchoolsWithAppeals['7biii). A level appeals: 2019-20'] + SchoolsWithAppeals['7aiii). GCSE appeals: 2019-20'])
		- (SchoolsWithAppeals['7bii). A level appeals: 2018-19'] + SchoolsWithAppeals['7aii). GCSE appeals: 2018-19'])
	)

	SchoolsWithAppeals['Percentage change in appeals 2019-2020'] = (
		(SchoolsWithAppeals['7biii). A level appeals: 2019-20'] + SchoolsWithAppeals['7aiii). GCSE appeals: 2019-20'])
		/ (SchoolsWithAppeals['7bii). A level appeals: 2018-19'] + SchoolsWithAppeals['7aii). GCSE appeals: 2018-19'])
	).fillna(0).replace(np.inf, 1)

	NumberWithDecreaseInAppeals = len(SchoolsWithAppeals.loc[SchoolsWithAppeals['Percentage change in appeals 2019-2020'] < 1].index)
	NumberWithIncreaseInAppeals = len(SchoolsWithAppeals.loc[SchoolsWithAppeals['Percentage change in appeals 2019-2020'] > 1].index)
	AveragePercentageChangeInAppeals = SchoolsWithAppeals['Percentage change in appeals 2019-2020'].mean()
	AverageRawChangeInAppeals = SchoolsWithAppeals['Raw change in appeals 2019-2020'].mean()

	return AnalysedData(
		schools_who_responded,
		SchoolsWithAppeals,
		NumberWhoResponded,
		NumberWhereAppealsAreApplicable,
		NumberWithIncreaseInAppeals,
		NumberWithDecreaseInAppeals,
		AveragePercentageChangeInAppeals,
		AverageRawChangeInAppeals
	)


def SchoolsWithJudicialReviews(schools_with_responses: pd.DataFrame) -> tuple[pd.DataFrame, int]:
	"""Plug in the schools with responses, get out the ones with judicial reviews and the number thereof"""

	schools_with_judicial_reviews = schools_with_responses.loc[
		(
				(pd.notna(schools_with_responses['8a). 2019-20 letters threatening judicial review over GCSE grades']))
				& (schools_with_responses['8a). 2019-20 letters threatening judicial review over GCSE grades'] > 0)
		)
		|
		(
			(pd.notna(schools_with_responses['8b). 2019-20 letters threatening judicial review over A level grades']))
			& (schools_with_responses['8b). 2019-20 letters threatening judicial review over A level grades'] > 0)
		)
	]

	NumberWhoReceivedJudicialReviews = len(schools_with_judicial_reviews.index)

	return schools_with_judicial_reviews, NumberWhoReceivedJudicialReviews
