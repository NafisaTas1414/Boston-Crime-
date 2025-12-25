-- Drop tables if they exist to allow re-creation
DROP TABLE IF EXISTS boston_crime;
DROP TABLE IF EXISTS crime_count_by_district_year;
DROP TABLE IF EXISTS crime_category_counts;

-- Create main crime table that stores raw crime reports
CREATE TABLE IF NOT EXISTS boston_crime (
    INCIDENT_NUMBER TEXT PRIMARY KEY,  -- Unique identifier for each crime report
    OFFENSE_CODE INTEGER,              -- Crime classification code
    OFFENSE_CODE_GROUP TEXT,           -- General offense category
    OFFENSE_DESCRIPTION TEXT,          -- Specific crime description
    DISTRICT TEXT,                     -- Police district where crime occurred
    REPORTING_AREA TEXT,                -- Smaller reporting unit
    SHOOTING TEXT,                      -- Indicates if shooting was involved (Y/N)
    OCCURRED_ON_DATE TEXT,              -- Date crime occurred
    YEAR INTEGER,                       -- Year of occurrence
    MONTH INTEGER,                      -- Month of occurrence
    DAY_OF_WEEK TEXT,                    -- Day crime occurred
    HOUR INTEGER,                        -- Hour of occurrence
    UCR_PART TEXT,                       -- FBI Uniform Crime Reporting classification
    STREET TEXT,                         -- Street where the crime happened
    Lat REAL,                            -- Latitude of the crime location
    Long REAL,                           -- Longitude of the crime location
    Location TEXT                        -- Full lcoation
);

-- Create table storing total crime counts per district per year
CREATE TABLE IF NOT EXISTS crime_count_by_district_year (
    DISTRICT TEXT,               -- Police district (e.g., A1, B2, C11)
    YEAR INTEGER,                -- Year the crimes occurred
    crime_count INTEGER DEFAULT 0, -- Total number of crimes in that district that year
    PRIMARY KEY (DISTRICT, YEAR)  -- Ensures uniqueness per district-year
);

-- Insert aggregated crime count data per district per year
INSERT INTO crime_count_by_district_year (DISTRICT, YEAR, crime_count)
SELECT
    DISTRICT,
    YEAR,
    COUNT(*) AS crime_count
FROM boston_crime
GROUP BY DISTRICT, YEAR
ORDER BY YEAR DESC, crime_count DESC;

-- Create table that categorizes crime types and stores crime counts per year
CREATE TABLE IF NOT EXISTS crime_category_counts (
    YEAR INTEGER,                -- Year of occurrence
    CRIME_CATEGORY TEXT,         -- Crime category classification
    crime_count INTEGER DEFAULT 0, -- Total count for this crime category that year
    PRIMARY KEY (YEAR, CRIME_CATEGORY)  -- Ensures unique year-category combination
);

-- Insert categorized crime data for each year
INSERT INTO crime_category_counts (YEAR, CRIME_CATEGORY, crime_count)
SELECT
    YEAR,
    CASE
        -- Fraud-related crimes
        WHEN OFFENSE_DESCRIPTION IN (
            'FRAUD - FALSE PRETENSE / SCHEME', 'FRAUD - IMPERSONATION', 'FRAUD - WELFARE',
            'FRAUD - CREDIT CARD / ATM FRAUD', 'FRAUD - WIRE'
        ) THEN 'Fraud'

        -- Crimes involving violence or threats
        WHEN OFFENSE_DESCRIPTION IN (
            'THREATS TO DO BODILY HARM', 'ASSAULT - SIMPLE', 'ASSAULT - AGGRAVATED',
            'ROBBERY', 'MURDER, NON-NEGLIGENT MANSLAUGHTER',
            'INTIMIDATING WITNESS', 'KIDNAPPING/CUSTODIAL KIDNAPPING/ ABDUCTION',
            'MANSLAUGHTER - NEGLIGENCE', 'MANSLAUGHTER - VEHICLE - NEGLIGENCE',
            'JUSTIFIABLE HOMICIDE', 'AFFRAY'
        ) THEN 'Violent Crimes'

        -- Theft and burglary-related offenses
        WHEN OFFENSE_DESCRIPTION IN (
            'LARCENY THEFT FROM BUILDING', 'LARCENY SHOPLIFTING', 'LARCENY THEFT FROM MV - NON-ACCESSORY',
            'LARCENY ALL OTHERS', 'LARCENY THEFT OF MV PARTS & ACCESSORIES', 'LARCENY THEFT OF BICYCLE',
            'AUTO THEFT', 'AUTO THEFT - MOTORCYCLE / SCOOTER', 'AUTO THEFT - LEASED/RENTED VEHICLE',
            'BURGLARY - COMMERCIAL', 'BURGLARY - RESIDENTIAL', 'STOLEN PROPERTY - BUYING / RECEIVING / POSSESSING'
        ) THEN 'Theft & Burglary'

        -- Drug and alcohol-related crimes
        WHEN OFFENSE_DESCRIPTION IN (
            'DRUGS - POSSESSION/ SALE/ MANUFACTURING/ USE', 'DRUGS - POSSESSION OF DRUG PARAPHERNALIA',
            'OPERATING UNDER THE INFLUENCE (OUI) ALCOHOL', 'OPERATING UNDER THE INFLUENCE (OUI) DRUGS',
            'LIQUOR/ALCOHOL - DRINKING IN PUBLIC', 'LIQUOR LAW VIOLATION', 'DRUNKENNESS'
        ) THEN 'Drug & Alcohol Crimes'

        -- Crimes related to motor vehicles
        WHEN OFFENSE_DESCRIPTION IN (
            'M/V - LEAVING SCENE - PROPERTY DAMAGE', 'M/V ACCIDENT - PERSONAL INJURY',
            'M/V ACCIDENT - PROPERTY DAMAGE', 'M/V ACCIDENT - INVOLVING PEDESTRIAN - INJURY',
            'M/V ACCIDENT - INVOLVING BICYCLE - NO INJURY', 'M/V ACCIDENT - INVOLVING BICYCLE - INJURY',
            'M/V ACCIDENT - OTHER', 'TOWED MOTOR VEHICLE'
        ) THEN 'Vehicle-Related Crimes'

        -- Crimes involving firearms or weapons
        WHEN OFFENSE_DESCRIPTION IN (
            'FIREARM/WEAPON - FOUND OR CONFISCATED', 'FIREARM/WEAPON - LOST',
            'FIREARM/WEAPON - ACCIDENTAL INJURY / DEATH', 'WEAPON VIOLATION - CARRY/ POSSESSING/ SALE/ TRAFFICKING/ OTHER',
            'EXPLOSIVES - POSSESSION OR USE'
        ) THEN 'Firearm & Weapons Crimes'

        -- Crimes related to prostitution or sexual offenses
        WHEN OFFENSE_DESCRIPTION IN (
            'PROSTITUTION', 'PROSTITUTION - SOLICITING', 'PROSTITUTION - ASSISTING OR PROMOTING',
            'SEXUAL ASSAULT'
        ) THEN 'Sex Crimes & Prostitution'

        -- Cases involving death investigations
        WHEN OFFENSE_DESCRIPTION IN (
            'SUDDEN DEATH', 'DEATH INVESTIGATION', 'SUICIDE / SUICIDE ATTEMPT'
        ) THEN 'Death Investigations'

        -- Arson and explosives-related incidents
        WHEN OFFENSE_DESCRIPTION IN ('ARSON', 'BOMB THREAT') THEN 'Arson & Explosives'

        -- Crimes involving animals
        WHEN OFFENSE_DESCRIPTION IN ('ANIMAL INCIDENTS (DOG BITES, LOST DOG, ETC)', 'ANIMAL ABUSE') THEN 'Animal Crimes'

        -- Cases involving a person being investigated
        WHEN OFFENSE_DESCRIPTION = 'INVESTIGATE PERSON' THEN 'Investigate Person'

        ELSE 'Uncategorized'  -- Ensures all crimes are categorized
    END AS CRIME_CATEGORY,
    COUNT(*) AS crime_count
FROM boston_crime
WHERE YEAR IS NOT NULL  -- Ensures only valid data is included
GROUP BY YEAR, CRIME_CATEGORY  -- Groups crime counts per year-category
ORDER BY YEAR DESC, crime_count DESC;

