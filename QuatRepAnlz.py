from edinet_xbrl.edinet_xbrl_parser import EdinetXbrlParser

## init parser
parser = EdinetXbrlParser()

## parse xbrl file and get data container
#xbrl_file_path = "./sample/jpcrp030000-asr-001_E33238-000_2018-03-31_01_2018-06-28.xbrl"
#xbrl_file_path = "./sample/jpcrp040300-q1r-001_E33238-000_2018-06-30_01_2018-08-13.xbrl"
#xbrl_file_path = "./sample/jpcrp040300-q3r-001_E32141-000_2018-04-30_01_2018-06-13.xbrl"
xbrl_file_path = "./sample/jpcrp040300-q2r-001_E32141-000_2018-01-31_01_2018-03-16.xbrl"
edinet_xbrl_object = parser.parse_file(xbrl_file_path)

## get value from container

ref         = ["売り上げ",           "営業利益",                  "経常利益"]
key         = ["jppfs_cor:NetSales", "jppfs_cor:OperatingIncome", "jppfs_cor:OrdinaryIncome"]

ref_fin             = [ "流動資産",               "固定資産",                   "流動負債",                     "固定負債"]
#key_fin         = ["jppfs_cor:CurrentAssets", "jppfs_cor:IntangibleAssets", "jppfs_cor:CurrentLiabilities", "jppfs_cor:LongTermLoansPayable"]
key_fin         = ["jppfs_cor:CurrentAssets", "jppfs_cor:NoncurrentAssets", "jppfs_cor:CurrentLiabilities", "jppfs_cor:NoncurrentLiabilities"]

ref_cf             = ["営業CF", "投資CF", "財務CF"]
#key_cf          = ["jppfs_cor:NetCashProvidedByUsedInOperatingActivities", "jppfs_cor:NetCashProvidedByUsedInInvestmentActivities", "jppfs_cor:NetCashProvidedByUsedInFinancingActivities"]  
key_cf          = ["jppfs_cor:NetCashProvidedByUsedInOperatingActivities", "jppfs_cor:NetCashProvidedByUsedInInvestmentActivities", "jppfs_cor:NetCashProvidedByUsedInFinancingActivities"]  

context_ref=["CurrentYTDDuration","CurrentQuarterInstant","CurrentYearDuration0","CurrentQuarterInstant_NonConsolidatedMember", "CurrentYTDDuration_NonConsolidatedMember"]


copname="jpcrp_cor:CompanyNameCoverPage"
contxtref="FilingDateInstant"
name=edinet_xbrl_object.get_data_by_context_ref(copname, contxtref).get_value()
print(name)

for i in range(len(key)):
    for j in range(len(context_ref)):
        dtobj= edinet_xbrl_object.get_data_by_context_ref(key[i], context_ref[j])
        if dtobj != None:
           val=dtobj.get_value()
           print(ref[i],":",val)
           break
for i in range(len(key_fin)):
    for j in range(len(context_ref)):
        dtobj= edinet_xbrl_object.get_data_by_context_ref(key_fin[i], context_ref[j])
        if dtobj != None:
           val=dtobj.get_value()
           print(ref_fin[i],":",val)
           break
for i in range(len(key_cf)):
    for j in range(len(context_ref)):
        dtobj= edinet_xbrl_object.get_data_by_context_ref(key_cf[i], context_ref[j])
        if dtobj != None:
           val=dtobj.get_value()
           print(ref_cf[i],":",val)
           break

#総資産
#key = "jppfs_cor:Assets"
#context_ref = "CurrentQuarterInstant"  #or CurrentQuarterInstant

#営業CF
#"jpcrp_cor:NetCashProvidedByUsedInOperatingActivitiesSummaryOfBusinessResults"
#"CurrentYearDuration"
#投資CF
#"jpcrp_cor:NetCashProvidedByUsedInInvestingActivitiesSummaryOfBusinessResults"
#"CurrentYearDuration"
#財務CF
#"jpcrp_cor:NetCashProvidedByUsedInFinancingActivitiesSummaryOfBusinessResults"
#"CurrentYearDuration"

#key="jpcrp040300-q1r_E33238-000:ManagementAnalysisOfFinancialPositionOperatingResultsAndCashFlowsTextBlock"
#context_ref ="FilingDateInstant"

