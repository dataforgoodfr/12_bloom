"""SCD implementation for dim_vessel/dim_zone

Revision ID: c02d2b79eab2
Revises: 5801cb8f1af5
Create Date: 2025-03-13 21:04:11.148024

"""
from alembic import op
import sqlalchemy as sa
from bloom.config import settings


# revision identifiers, used by Alembic.
revision = 'c02d2b79eab2'
down_revision = '5801cb8f1af5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create SCD columns for dim_vessel and dim_zone with existing data (nullable)
    op.add_column("dim_vessel",sa.Column("scd_start",sa.DateTime(timezone=True),nullable=True))
    op.add_column("dim_vessel",sa.Column("scd_end",sa.DateTime(timezone=True),nullable=True))
    op.add_column("dim_vessel",sa.Column("scd_active",sa.Boolean,nullable=True))
    op.add_column("dim_vessel",sa.Column("key",sa.String,nullable=True))
    
    op.add_column("dim_zone",sa.Column("scd_start",sa.DateTime(timezone=True),nullable=True))
    op.add_column("dim_zone",sa.Column("scd_end",sa.DateTime(timezone=True),nullable=True))
    op.add_column("dim_zone",sa.Column("scd_active",sa.Boolean,nullable=True))
    op.add_column("dim_zone",sa.Column("key",sa.String,nullable=True))

    # Initialize scd_column values
    op.execute( (f"update dim_vessel set scd_start = '{settings.scd_past_limit.isoformat()}',"
                 f"scd_end = '{settings.scd_future_limit.isoformat()}',"
                 f"scd_active = false,"
                 f"key = (CASE WHEN imo IS NOT NULL THEN imo::varchar(255) ELSE cfr END)"
                 ))
    op.execute( (f"update dim_vessel "
                 f"set scd_active = true "
                 f"where tracking_status = 'active'"
                 ))
    
    op.execute( (f"update dim_zone set scd_start = '{settings.scd_past_limit.isoformat()}',"
                 f"scd_end = '{settings.scd_future_limit.isoformat()}',"
                 f"scd_active = true,"
                 f"key = COALESCE(category,'')||'/'||COALESCE(sub_category,'')||'/'||name"
                 ))
    
    # Set scd columns not nullable after init
    op.alter_column("dim_vessel","scd_start",nullable=False)
    op.alter_column("dim_vessel","scd_end",nullable=False)
    op.alter_column("dim_vessel","scd_active",nullable=False)
    op.alter_column("dim_vessel","key",nullable=False)
    
    op.alter_column("dim_zone","scd_start",nullable=False)
    op.alter_column("dim_zone","scd_end",nullable=False)
    op.alter_column("dim_zone","scd_active",nullable=False)
    op.alter_column("dim_zone","key",nullable=False)

    # Adding vessel_mapping table
    op.create_table("dim_vessel_mapping",
                    sa.Column("id", sa.Integer, primary_key=True),
                    sa.Column("imo", sa.Integer),
                    sa.Column("mmsi", sa.Integer),
                    sa.Column("name", sa.String),
                    sa.Column("country", sa.String),
                    
                    sa.Column("same_imo", sa.ARRAY(sa.Integer)),
                    sa.Column("same_mmsi", sa.ARRAY(sa.Integer)),
                    sa.Column("same_name", sa.ARRAY(sa.Integer)),
                    sa.Column("same_country", sa.ARRAY(sa.Integer)),

                    sa.Column("appearance_first",sa.DateTime(timezone=True)),
                    sa.Column("appearance_last",sa.DateTime(timezone=True)),

                    sa.Column("mapping_auto", sa.Integer, sa.ForeignKey("dim_vessel.id"), nullable=True),
                    sa.Column("mapping_manual", sa.Integer, sa.ForeignKey("dim_vessel.id"), nullable=True),
                    sa.Column("vessel_id", sa.Integer,sa.ForeignKey("dim_vessel.id"), nullable=True),

                    sa.Column("scd_start",sa.DateTime(timezone=True)),
                    sa.Column("scd_end",sa.DateTime(timezone=True)),
                    sa.Column("scd_active",sa.Boolean),
                    sa.Column(
                        "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(),
                    ),
                    sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now())
                    )
    # Initialization of dim_vessel_mapping data from current spire_ais_data
    op.execute("""
        insert into dim_vessel_mapping (imo,mmsi,name,country)
        select distinct sad.vessel_imo , sad.vessel_mmsi, sad.vessel_name ,
        case sad.vessel_flag 
        WHEN 'AF' THEN 'AFG'
        WHEN 'AL' THEN 'ALB'
        WHEN 'AQ' THEN 'ATA'
        WHEN 'DZ' THEN 'DZA'
        WHEN 'AS' THEN 'ASM'
        WHEN 'AD' THEN 'AND'
        WHEN 'AO' THEN 'AGO'
        WHEN 'AG' THEN 'ATG'
        WHEN 'AZ' THEN 'AZE'
        WHEN 'AR' THEN 'ARG'
        WHEN 'AU' THEN 'AUS'
        WHEN 'AT' THEN 'AUT'
        WHEN 'BS' THEN 'BHS'
        WHEN 'BH' THEN 'BHR'
        WHEN 'BD' THEN 'BGD'
        WHEN 'AM' THEN 'ARM'
        WHEN 'BB' THEN 'BRB'
        WHEN 'BE' THEN 'BEL'
        WHEN 'BM' THEN 'BMU'
        WHEN 'BT' THEN 'BTN'
        WHEN 'BO' THEN 'BOL'
        WHEN 'BA' THEN 'BIH'
        WHEN 'BW' THEN 'BWA'
        WHEN 'BV' THEN 'BVT'
        WHEN 'BR' THEN 'BRA'
        WHEN 'BZ' THEN 'BLZ'
        WHEN 'IO' THEN 'IOT'
        WHEN 'SB' THEN 'SLB'
        WHEN 'VG' THEN 'VGB'
        WHEN 'BN' THEN 'BRN'
        WHEN 'BG' THEN 'BGR'
        WHEN 'MM' THEN 'MMR'
        WHEN 'BI' THEN 'BDI'
        WHEN 'BY' THEN 'BLR'
        WHEN 'KH' THEN 'KHM'
        WHEN 'CM' THEN 'CMR'
        WHEN 'CA' THEN 'CAN'
        WHEN 'CV' THEN 'CPV'
        WHEN 'KY' THEN 'CYM'
        WHEN 'CF' THEN 'CAF'
        WHEN 'LK' THEN 'LKA'
        WHEN 'TD' THEN 'TCD'
        WHEN 'CL' THEN 'CHL'
        WHEN 'CN' THEN 'CHN'
        WHEN 'TW' THEN 'TWN'
        WHEN 'CX' THEN 'CXR'
        WHEN 'CC' THEN 'CCK'
        WHEN 'CO' THEN 'COL'
        WHEN 'KM' THEN 'COM'
        WHEN 'YT' THEN 'MYT'
        WHEN 'CG' THEN 'COG'
        WHEN 'CD' THEN 'COD'
        WHEN 'CK' THEN 'COK'
        WHEN 'CR' THEN 'CRI'
        WHEN 'HR' THEN 'HRV'
        WHEN 'CU' THEN 'CUB'
        WHEN 'CY' THEN 'CYP'
        WHEN 'CZ' THEN 'CZE'
        WHEN 'BJ' THEN 'BEN'
        WHEN 'DK' THEN 'DNK'
        WHEN 'DM' THEN 'DMA'
        WHEN 'DO' THEN 'DOM'
        WHEN 'EC' THEN 'ECU'
        WHEN 'SV' THEN 'SLV'
        WHEN 'GQ' THEN 'GNQ'
        WHEN 'ET' THEN 'ETH'
        WHEN 'ER' THEN 'ERI'
        WHEN 'EE' THEN 'EST'
        WHEN 'FO' THEN 'FRO'
        WHEN 'FK' THEN 'FLK'
        WHEN 'GS' THEN 'SGS'
        WHEN 'FJ' THEN 'FJI'
        WHEN 'FI' THEN 'FIN'
        WHEN 'AX' THEN 'ALA'
        WHEN 'FR' THEN 'FRA'
        WHEN 'GF' THEN 'GUF'
        WHEN 'PF' THEN 'PYF'
        WHEN 'TF' THEN 'ATF'
        WHEN 'DJ' THEN 'DJI'
        WHEN 'GA' THEN 'GAB'
        WHEN 'GE' THEN 'GEO'
        WHEN 'GM' THEN 'GMB'
        WHEN 'PS' THEN 'PSE'
        WHEN 'DE' THEN 'DEU'
        WHEN 'GH' THEN 'GHA'
        WHEN 'GI' THEN 'GIB'
        WHEN 'KI' THEN 'KIR'
        WHEN 'GR' THEN 'GRC'
        WHEN 'GL' THEN 'GRL'
        WHEN 'GD' THEN 'GRD'
        WHEN 'GP' THEN 'GLP'
        WHEN 'GU' THEN 'GUM'
        WHEN 'GT' THEN 'GTM'
        WHEN 'GN' THEN 'GIN'
        WHEN 'GY' THEN 'GUY'
        WHEN 'HT' THEN 'HTI'
        WHEN 'HM' THEN 'HMD'
        WHEN 'VA' THEN 'VAT'
        WHEN 'HN' THEN 'HND'
        WHEN 'HK' THEN 'HKG'
        WHEN 'HU' THEN 'HUN'
        WHEN 'IS' THEN 'ISL'
        WHEN 'IN' THEN 'IND'
        WHEN 'ID' THEN 'IDN'
        WHEN 'IR' THEN 'IRN'
        WHEN 'IQ' THEN 'IRQ'
        WHEN 'IE' THEN 'IRL'
        WHEN 'IL' THEN 'ISR'
        WHEN 'IT' THEN 'ITA'
        WHEN 'CI' THEN 'CIV'
        WHEN 'JM' THEN 'JAM'
        WHEN 'JP' THEN 'JPN'
        WHEN 'KZ' THEN 'KAZ'
        WHEN 'JO' THEN 'JOR'
        WHEN 'KE' THEN 'KEN'
        WHEN 'KP' THEN 'PRK'
        WHEN 'KR' THEN 'KOR'
        WHEN 'KW' THEN 'KWT'
        WHEN 'KG' THEN 'KGZ'
        WHEN 'LA' THEN 'LAO'
        WHEN 'LB' THEN 'LBN'
        WHEN 'LS' THEN 'LSO'
        WHEN 'LV' THEN 'LVA'
        WHEN 'LR' THEN 'LBR'
        WHEN 'LY' THEN 'LBY'
        WHEN 'LI' THEN 'LIE'
        WHEN 'LT' THEN 'LTU'
        WHEN 'LU' THEN 'LUX'
        WHEN 'MO' THEN 'MAC'
        WHEN 'MG' THEN 'MDG'
        WHEN 'MW' THEN 'MWI'
        WHEN 'MY' THEN 'MYS'
        WHEN 'MV' THEN 'MDV'
        WHEN 'ML' THEN 'MLI'
        WHEN 'MT' THEN 'MLT'
        WHEN 'MQ' THEN 'MTQ'
        WHEN 'MR' THEN 'MRT'
        WHEN 'MU' THEN 'MUS'
        WHEN 'MX' THEN 'MEX'
        WHEN 'MC' THEN 'MCO'
        WHEN 'MN' THEN 'MNG'
        WHEN 'MD' THEN 'MDA'
        WHEN 'ME' THEN 'MNE'
        WHEN 'MS' THEN 'MSR'
        WHEN 'MA' THEN 'MAR'
        WHEN 'MZ' THEN 'MOZ'
        WHEN 'OM' THEN 'OMN'
        WHEN 'NA' THEN 'NAM'
        WHEN 'NR' THEN 'NRU'
        WHEN 'NP' THEN 'NPL'
        WHEN 'NL' THEN 'NLD'
        WHEN 'CW' THEN 'CUW'
        WHEN 'AW' THEN 'ABW'
        WHEN 'SX' THEN 'SXM'
        WHEN 'BQ' THEN 'BES'
        WHEN 'NC' THEN 'NCL'
        WHEN 'VU' THEN 'VUT'
        WHEN 'NZ' THEN 'NZL'
        WHEN 'NI' THEN 'NIC'
        WHEN 'NE' THEN 'NER'
        WHEN 'NG' THEN 'NGA'
        WHEN 'NU' THEN 'NIU'
        WHEN 'NF' THEN 'NFK'
        WHEN 'NO' THEN 'NOR'
        WHEN 'MP' THEN 'MNP'
        WHEN 'UM' THEN 'UMI'
        WHEN 'FM' THEN 'FSM'
        WHEN 'MH' THEN 'MHL'
        WHEN 'PW' THEN 'PLW'
        WHEN 'PK' THEN 'PAK'
        WHEN 'PA' THEN 'PAN'
        WHEN 'PG' THEN 'PNG'
        WHEN 'PY' THEN 'PRY'
        WHEN 'PE' THEN 'PER'
        WHEN 'PH' THEN 'PHL'
        WHEN 'PN' THEN 'PCN'
        WHEN 'PL' THEN 'POL'
        WHEN 'PT' THEN 'PRT'
        WHEN 'GW' THEN 'GNB'
        WHEN 'TL' THEN 'TLS'
        WHEN 'PR' THEN 'PRI'
        WHEN 'QA' THEN 'QAT'
        WHEN 'RE' THEN 'REU'
        WHEN 'RO' THEN 'ROU'
        WHEN 'RU' THEN 'RUS'
        WHEN 'RW' THEN 'RWA'
        WHEN 'BL' THEN 'BLM'
        WHEN 'SH' THEN 'SHN'
        WHEN 'KN' THEN 'KNA'
        WHEN 'AI' THEN 'AIA'
        WHEN 'LC' THEN 'LCA'
        WHEN 'MF' THEN 'MAF'
        WHEN 'PM' THEN 'SPM'
        WHEN 'VC' THEN 'VCT'
        WHEN 'SM' THEN 'SMR'
        WHEN 'ST' THEN 'STP'
        WHEN 'SA' THEN 'SAU'
        WHEN 'SN' THEN 'SEN'
        WHEN 'RS' THEN 'SRB'
        WHEN 'SC' THEN 'SYC'
        WHEN 'SL' THEN 'SLE'
        WHEN 'SG' THEN 'SGP'
        WHEN 'SK' THEN 'SVK'
        WHEN 'VN' THEN 'VNM'
        WHEN 'SI' THEN 'SVN'
        WHEN 'SO' THEN 'SOM'
        WHEN 'ZA' THEN 'ZAF'
        WHEN 'ZW' THEN 'ZWE'
        WHEN 'ES' THEN 'ESP'
        WHEN 'SS' THEN 'SSD'
        WHEN 'SD' THEN 'SDN'
        WHEN 'EH' THEN 'ESH'
        WHEN 'SR' THEN 'SUR'
        WHEN 'SJ' THEN 'SJM'
        WHEN 'SZ' THEN 'SWZ'
        WHEN 'SE' THEN 'SWE'
        WHEN 'CH' THEN 'CHE'
        WHEN 'SY' THEN 'SYR'
        WHEN 'TJ' THEN 'TJK'
        WHEN 'TH' THEN 'THA'
        WHEN 'TG' THEN 'TGO'
        WHEN 'TK' THEN 'TKL'
        WHEN 'TO' THEN 'TON'
        WHEN 'TT' THEN 'TTO'
        WHEN 'AE' THEN 'ARE'
        WHEN 'TN' THEN 'TUN'
        WHEN 'TR' THEN 'TUR'
        WHEN 'TM' THEN 'TKM'
        WHEN 'TC' THEN 'TCA'
        WHEN 'TV' THEN 'TUV'
        WHEN 'UG' THEN 'UGA'
        WHEN 'UA' THEN 'UKR'
        WHEN 'MK' THEN 'MKD'
        WHEN 'EG' THEN 'EGY'
        WHEN 'GB' THEN 'GBR'
        WHEN 'GG' THEN 'GGY'
        WHEN 'JE' THEN 'JEY'
        WHEN 'IM' THEN 'IMN'
        WHEN 'TZ' THEN 'TZA'
        WHEN 'US' THEN 'USA'
        WHEN 'VI' THEN 'VIR'
        WHEN 'BF' THEN 'BFA'
        WHEN 'UY' THEN 'URY'
        WHEN 'UZ' THEN 'UZB'
        WHEN 'VE' THEN 'VEN'
        WHEN 'WF' THEN 'WLF'
        WHEN 'WS' THEN 'WSM'
        WHEN 'YE' THEN 'YEM'
        WHEN 'ZM' THEN 'ZMB'
        else '???' END
        from spire_ais_data sad
        """)
    # Add vessel_mapping for past excursion without spire_ais_data (archive,...)
    op.execute("""
        insert into dim_vessel_mapping (imo,mmsi,"name",country)
        (select imo, mmsi, ship_name, country_iso3
        from fct_excursion
        join dim_vessel on fct_excursion.vessel_id = dim_vessel.id
        where dim_vessel.id not in (select vessel_id from dim_vessel_mapping))
    """)
    op.execute("""
        update dim_vessel_mapping 
        set mapping_auto = (select id from dim_vessel where dim_vessel.mmsi = dim_vessel_mapping.mmsi and dim_vessel.tracking_status='active'),
        vessel_id = (select id from dim_vessel where dim_vessel.mmsi = dim_vessel_mapping.mmsi and dim_vessel.tracking_status='active'),
        scd_start = (select scd_start from dim_vessel where dim_vessel.mmsi = dim_vessel_mapping.mmsi and dim_vessel.tracking_status='active'),
        scd_end = (select scd_end from dim_vessel where dim_vessel.mmsi = dim_vessel_mapping.mmsi and dim_vessel.tracking_status='active'),
        scd_active = (select scd_active from dim_vessel where dim_vessel.mmsi = dim_vessel_mapping.mmsi and dim_vessel.tracking_status='active');   """)
    # Adding vessel_mapping_id to fct_excursion
    op.add_column("fct_excursion",
                  sa.Column('vessel_mapping_id',
                                sa.Integer,
                                sa.ForeignKey("dim_vessel_mapping.id"),
                                nullable=True))

    # Initializing fct_excursion.vessel_mapping_id from dim_vessel_mapping.auto_mapping
    op.execute("""
    update fct_excursion 
    set vessel_mapping_id =
               ( select id from dim_vessel_mapping
                    where vessel_id = fct_excursion.vessel_id limit 1);
    """)

    op.alter_column("fct_excursion","vessel_mapping_id",nullable=False)


def downgrade() -> None:
    op.drop_column("fct_excursion","vessel_mapping_id")
    op.drop_table("dim_vessel_mapping")

    op.drop_column("dim_zone","scd_start")
    op.drop_column("dim_zone","scd_end")
    op.drop_column("dim_zone","scd_active")
    op.drop_column("dim_zone","key")

    op.drop_column("dim_vessel","scd_start")
    op.drop_column("dim_vessel","scd_end")
    op.drop_column("dim_vessel","scd_active")
    op.drop_column("dim_vessel","key")
    pass
