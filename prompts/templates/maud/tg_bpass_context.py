BUILDNOW_CONTEXT = """
BuildNow is a Unified Online Building And Layout Approval System And Cloud Based Automated Building Drawing Scrutiny System designed to streamline and expedite the building plan approval process in Telangana. The system allows applicants to submit their building plans and related documents online, track the status of their applications, and receive approvals digitally.

The different types of applications include:
1. Building Permission - building permits for residential, commercial, industrial, etc buildings
2. Layout Permission - Subdivision and development of land plots
   - Layout with Housing Under Gated Community (With Compound Wall)
   - Layout with Housing without Gated and Community
   - Layout Open Plot
3. Occupancy Certificate - Post-construction occupancy approvals
4. Compound Wall - Standalone compound wall permissions

Note: Layout with Housing Under Gated Community (With Compound Wall) & Layout with Housing without Gated and Community will have both building permission & layout permission.

There are three categories of processing applications in BuildNow:
1. 'Instant Registration (IR)' is for buildings less than 75 sq yards in plot area and less than 7 meters of height for Residential Buildings. Process: workflow with minimal verification. Timeline: 15 days. Features: No auto-scrutiny, No payment, direct department verification.
2. 'Instant Approval (IA)' is for buildings less than 600 sq yards in plot area and less than 10 meters of height for Residential Buildings. Process: workflow with streamlined verification. Timeline: 15 days. Features: reduced documentation, fast-track processing, Payment included.
3. 'Single Window (SW)' is for buildings more than 600 sq yards OR more than 10 meters of height OR non-residential OR layouts OR compound walls. Process: workflow with comprehensive verification. Timeline: 21 days. Features: Auto-scrutiny, mortgage verification, TDR processing, relinquishment procedures.

The authorities which process the applications are:
- HMDA, GHMC, and DTCP, which come under the Municipal Administration and Urban Development Department, Government of Telangana.
- Along with these, some applications also require NoC from line departments like Revenue (Land ownership), Fire (Fire safety clearances for larger buildings), Irrigation (Water body and drainage clearances), Title (Property title verification), and Pollution (Environmental clearances), etc.

For all processing categories, applications go through various stages. The complete stages are as below:

<User Application Stages>

Common Initial Stages (All Categories):
1. "Draft" stage: The applicant creates and fills the application with personal and plot details, and uploads the CAD drawing file if required. The application remains in this stage until submission.

Single Window System Specific Stages:
2. "Draft In Progress" stage: Upon submission, the drawing file is processed by a cloud-based auto-scrutiny system (only for single window applications).
3. "Processing Fee Pending" stage: Initial fee payment required (only for single window applications).

Scrutiny Stages (Single Window Only):
4. "Scrutiny Failed" stage: Auto-scrutiny failed, requires CAD file correction and resubmission.
5. "Scrutiny Successful" stage: Auto-scrutiny passed successfully, proceeding to verification stages.
6. "Scrutiny Key Generated" stage: Manual override for failed scrutiny cases.
7. "Shortfall Scrutiny Failed" stage: Scrutiny failed after shortfall correction.

Verification and Processing Stages (All Categories):
8. "Under Department Verification" stage: Primary authority officer review in progress.
9. "Other Department Verification In Progress" stage: Line department approvals pending.
10. "Payment Pending" stage: Final fee payment required before submission is required for Instant Approval. In case of single window fee payment after officer review
11. "Revised Payment Pending" stage: additional amount to be paid after officer review.

Issue Resolution Stages:
12. "Shortfall" stage: Corrections/additional documents required from applicant.
13. "Initiating Resubmission" stage: Application resubmission in progress after corrections.

Specialized Processing Stages (Single Window):
14. "Submit TDR Details" stage: Transferable Development Rights payment option.
15. "Awaiting TDR Confirmation" stage: TDR bank and owner confirmation pending.
16. "Issue in TDR Details" stage: TDR documentation issues requiring correction.
17. "Mortgage & Other Info pending" stage: Post-payment mortgage details submission required.
18. "Under Mortgage & Other Info Verification" stage: Officer verification of mortgage details.
19. "Issue in Mortgage & Other Info Details" stage: Mortgage documentation corrections needed.
20. "Relinquishment Details Pending" stage: Relinquishment deed submission required (layouts).
21. "Under Relinquishment Details Verification" stage: Officer verification of relinquishment.
22. "Issue in Relinquishment Details" stage: Relinquishment documentation issues.

Final Stages:
23. "Proceedings Generated" stage: Final approval documents ready for issuance (only for Single Window) .
24. "Approved" stage: Application successfully approved (only for Instant Approval, Instant Registration).
25. "Rejected" stage: Application rejected by authorities.
26. "Application On-Hold" stage: Temporary suspension for administrative reasons.

</User Application Stages>

As mentioned above, when the User Application reaches verification stages, Workflow Requests are initiated for the Authority selected in the application. For HMDA, GHMC, and DTCP, there are four levels of officers to process the Workflow Request. Each Workflow Request goes through several workflow stages as described below:

In HMDA, GHMC, and DTCP, there are multiple officer-facing workflow stages where officers from four levels are involved in processing applications.

<Officer Levels and Tasks>

Level 1 (Multiple specialized officers):
1. Technical Verification:
   - HMDA: APO/JPO (Assistant Planning Officer/Junior Planning Officer)
   - GHMC: ACP (Assistant City Planner)
   - DTCP: STO (Site Technical Officer)
2. Title Verification:
   - HMDA: Tehsildar
   - GHMC: ACP (Assistant City Planner)
   - DTCP: TVO (Title Verification Officer)
3. Site Inspection:
   - All authorities: SI (Site Inspector)
4. Specialized Officers:
   - DTCP: TTVO (Title & Technical Verification Officer)

Level 2 (1 officer):
- HMDA: Planning Officer
- GHMC: City Planner
- DTCP: L2 Officer

Level 3 (1 officer):
- HMDA: Director
- GHMC: Chief City Planner
- DTCP: L3 Officer

Level 4 (1 officer):
- HMDA: Metropolitan Commissioner
- GHMC: GHMC Commissioner
- DTCP: L4 Officer

</Officer Levels and Tasks>

<Officer-Facing Workflow Stages>

Verification Stages by Level:
1. Under L1 Verification
   - All Level 1 officers complete their respective specialized tasks
   - Includes parallel processing stages:
     * Under L1(STO)/L1(TVO) Verification: Parallel L1 specialized processing
     * Under (STO) Verification: Individual STO processing
     * Under (TVO) Verification: Individual TVO processing
     * Under (TTVO) Verification: Technical & Title officer processing
     * Under (SI) Verification: Site Inspector processing
     * Under L1(APO/JPO)/L1(TVO) Verification: HMDA parallel processing
     * Under L1(ACP)/L1(TVO) Verification: GHMC parallel processing
     * Under L1(SI)/L1(TTVO) Verification: DTCP parallel processing
   - Upon completion, moves to "Under L2 Verification"

2. Under L2 Verification
   - Level 2 officer examines Level 1 remarks and chooses:
     A. Forward to Level 3 (moves to "Under L3 Verification")
     B. Send back for re-verification (moves to "Under L1 Verification")
     C. Mark as Shortfall (moves to "Shortfall" stage)

3. Under L3 Verification
   - Level 3 officer examines all previous remarks and chooses:
     A. Forward to Level 4 (moves to "Under L4 Verification")
     B. Send back for re-verification (moves to "Under L2 Verification")
     C. Mark as Shortfall (moves to "Shortfall" stage)

4. Under L4 Verification
   - Level 4 officer examines all previous remarks and chooses:
     A. Approve (moves to "Final Payment Pending" stage)
     B. Reject (moves to "Rejection Verification by L2" stage)
     C. Send back for re-verification (moves to "Under L3 Verification")

Processing Decision Stages:
5. On Hold For Line Dept Remarks
   - Awaiting line department inputs before proceeding

6. Shortfall
   - Officer-identified deficiencies requiring correction

7. Rejected
   - Officer rejection decision

8. Approved
   - Officer approval decision

9. Rejection Verification by L2
   - L2 officer confirms rejection decision

Payment and Fee Stages:
10. Final Payment Pending
    - Final fee payment required after approval

11. Final Payment Paid
    - Payment received, proceeding to final steps

12. Revised Fee Intimation Sent
    - Fee revision notification issued

Post-Payment Verification (Single Window):
13. Under Post Payment Details Verification by L1/L2/L3
    - Post-payment document verification at different levels

14. Post Payment Details Shortfall
    - Issues in post-payment documentation

15. Issue Proceedings by L2
    - L2 officer issues final proceedings

TDR Processing Stages:
16. Awaiting TDR Confirmation
    - TDR confirmation pending

17. Verify TDR Details
    - Officer TDR verification

18. Verify TDR Details by L2
    - L2 officer TDR verification

19. TDR Accepted by Owner
    - Owner acceptance of TDR terms

20. TDR Shortfall
    - TDR documentation issues

Final Processing:
21. Proceedings Generated
    - Final documents generated

22. Application On-Hold
    - Administrative hold

Rejection Categories:
23. Rejected
    - Standard rejection

24. Rejected with Refund
    - Rejection with fee refund

25. Rejected without Refund
    - Rejection without fee refund

26. Reject with Refund
    - Alternative rejection with refund

</Officer-Facing Workflow Stages>

Note: The workflow stages follow similar patterns across HMDA, GHMC, and DTCP, with differences in officer designations and some authority-specific processes. Single Window applications have additional complexity with TDR processing, mortgage verification, and relinquishment procedures that are not present in Instant Registration or Instant Approval categories.

"""