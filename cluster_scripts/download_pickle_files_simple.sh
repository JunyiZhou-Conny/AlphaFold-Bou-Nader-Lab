#!/bin/bash

# Simple script to download pickle files for protein accessions
# Extract accessions from CSV: awk -F',' 'NR>1 {print $2}' full_robust_workflow.csv

# Configuration - ADJUST THESE PATHS FOR YOUR CLUSTER
DEST_DIR="/data7/Conny/Projects/Dicer_685/JackFeatureDB_Pickle"
LOG_FILE="/data7/Conny/Projects/Dicer_685/JackFeatureDB_Pickledownload_pickle_files.log"
ERROR_LOG="/data7/Conny/Projects/Dicer_685/JackFeatureDB_Pickledownload_pickle_files_errors.log"

# Create destination directory
mkdir -p "$DEST_DIR"

# Initialize logs
echo "=== Pickle File Download Log - Started at $(date) ===" > "$LOG_FILE"
echo "=== Error Log - Started at $(date) ===" > "$ERROR_LOG"

# Protein accessions extracted from CSV (full_robust_workflow.csv)
ACCESSIONS=(
    "Q15633" "O14965" "P26373" "O95793" "Q08211" "Q12905" "O75569" "P05388" "P15880" "Q9NUL3"
    "P17844" "P26641" "P13639" "P06733" "P22626" "P07910" "Q14103" "P11142" "P20700" "Q15365"
    "Q15366" "P61353" "P39023" "P60866" "P62851" "P62701" "P46781" "P11387" "Q13263" "P24752"
    "P08243" "P27824" "P78371" "P49368" "Q99832" "P50990" "P23528" "P55060" "P19525" "Q14152"
    "O00303" "P51114" "Q13283" "Q9UN86" "Q9BZE4" "P55084" "P55795" "P31942" "P08238" "Q12906"
    "P33993" "P33992" "P33993" "Q9HCE1" "Q15233" "O43175" "P14618" "Q99575" "Q06830" "P62906"
    "P62913" "P30050" "P62899" "P18077" "P36578" "P62424" "P32969" "P04843" "P62263" "P62244"
    "P61247" "Q9Y230" "P05141" "P49458" "Q9BXP5" "P84103" "Q96SI9" "O60506" "P17987" "Q14258"
    "P67809" "P16989" "P62258" "Q9UKV3" "P63261" "O00116" "Q8TES7" "O75964" "Q96GD4" "Q07021"
    "Q9Y696" "Q15417" "Q10570" "P19784" "Q13618" "Q92841" "Q9NVP1" "O00571" "Q9UJV9" "Q9BQ39"
    "P26196" "Q9UNQ2" "O60884" "Q9UKV8" "P38919" "Q04637" "P15311" "P63244" "Q13823" "P16403"
    "P62805" "Q96FZ2" "P52597" "P14866" "P52272" "Q00839" "Q1KMD3" "P51659" "P0DMV8" "P34932"
    "O00425" "Q92945" "Q14739" "P02545" "Q03252" "Q9Y383" "O95232" "Q9NX58" "P31153" "Q15648"
    "Q9BYG3" "P52701" "P11586" "P35579" "P19338" "Q8WTT2" "P06748" "Q9UQ80" "Q13310" "Q86U42"
    "P07737" "Q9NQ55" "P30044" "P30041" "P78527" "Q9UHX1" "P63244" "Q96PK6" "Q96T37" "Q14498"
    "P38159" "P35251" "P27694" "P15927" "P27635" "P40429" "P50914" "P61313" "P18621" "P62829"
    "P62750" "P83731" "P46779" "P62888" "P42766" "P62917" "P62280" "P62277" "P62249" "P08708"
    "P39019" "P23396" "P46782" "P62753" "P08865" "O43159" "O76021" "Q15424" "O00422" "Q8NC51"
    "Q13435" "P12236" "Q7KZF4" "P09012" "Q01130" "Q9Y5B9" "Q13148" "Q16832" "P42166" "P11388"
    "Q02880" "Q13595" "Q8IZ69" "Q9Y4A5" "P22314" "Q14157" "Q93009" "P45880" "P08670" "P13010"
    "Q9NY61" "P61221" "Q8NE71" "Q9ULW3" "P53396" "P24666" "P68133" "P60709" "P55265" "Q9H2P0"
    "Q8WYP5" "P23526" "O43823" "P54886" "Q86V81" "Q96CW1" "O60306" "Q9NWB6" "Q92974" "Q66PJ3"
    "Q8N3C0" "Q9NVI7" "P16615" "P36542" "Q9NRL2" "Q9UIG0" "O75934" "Q9P287" "Q9NYF8" "Q14692"
    "Q12830" "Q8TDN6" "O43684" "Q13895" "Q9Y224" "Q53F19" "Q9Y3I0" "O76075" "Q14444" "Q6P1N0"
    "Q8IX12" "Q9H6F5" "O75909" "P50991" "P48643" "P40227" "O60508" "Q99459" "Q6P1J9" "Q03701"
    "Q7Z7K6" "Q13112" "Q14839" "Q8IWX8" "Q9Y3Y2" "Q14677" "Q00610" "Q8NFW8" "P53621" "P53618"
    "P35606" "Q9BZJ0" "O75390" "O75534" "P68400" "Q12996" "P49711" "P17812" "Q9NXE8" "P51398"
    "Q96EP5" "Q9NV06" "Q16531" "Q92499" "Q13206" "Q9NR30" "Q9BUQ8" "Q9GZR7" "Q96GQ7" "Q9H8H2"
    "Q13838" "Q86XP3" "Q7L014" "Q9H0S4" "Q9Y6V7" "Q8N8A6" "Q9Y2R4" "Q8TDD1" "Q9NY93" "O95786"
    "P35659" "O43143" "Q7Z478" "Q7L2E3" "Q9H2U1" "Q8IY37" "Q14562" "Q9Y2L1" "O60832" "Q96EY1"
    "Q8WXX5" "P26358" "Q5QJE6" "Q99848" "P68104" "Q5VTE0" "Q15029" "P05198" "P05198" "Q99613"
    "O15371" "Q13347" "Q9Y262" "P60842" "P78344" "O60841" "P56537" "Q15717" "P84090" "Q01780"
    "Q9NPD3" "Q15024" "Q9NZB2" "Q9UK61" "Q52LJ0" "P49327" "P22087" "P39748" "Q6UN15" "Q13451"
    "Q13045" "Q8IY81" "Q96AE4" "P22102" "Q86YP4" "Q06210" "Q9NZM5" "Q49A26" "Q9BVP2" "Q9NVN8"
    "Q9BQ67" "P78347" "Q12789" "Q9Y5Q8" "P07305" "Q92522" "Q71UI9" "P16104" "O75367" "P84243"
    "P51610" "Q13547" "Q00341" "Q9H583" "Q9NRZ9" "Q02539" "P16401" "P16402" "Q96KK5" "Q99880"
    "Q16777" "Q71DI3" "Q14527" "P52926" "Q13151" "P09651" "P51991" "Q99729" "P31943" "P61978"
    "O43390" "Q9BUJ2" "O14979" "Q5SSJ5" "Q53GQ0" "P07900" "Q0VDF9" "Q7Z6Z7" "Q9Y4L1" "Q9NZI8"
    "Q13123" "O95163" "Q8TCT7" "Q9NQS7" "Q9H9L3" "O60341" "Q07666" "Q15397" "Q69YN4" "Q14807"
    "Q02241" "O95239" "P52292" "O60684" "Q14974" "P01116" "Q8N9T8" "Q13601" "Q6PKG0" "Q92615"
    "Q4G0J3" "Q9P2J5" "Q9Y4W2" "P49916" "Q9H9Z2" "P42704" "Q9NQ29" "P43243" "P25205" "P33991"
    "Q14566" "Q14676" "Q9NU22" "Q9BU76" "O00566" "P49959" "Q9Y2R9" "Q9UKD2" "P43246" "Q13330"
    "O94776" "Q86UE4" "Q6UB35" "Q9BQG0" "Q9P2K5" "P19105" "O00159" "Q9UM54" "Q13459" "Q5VVJ2"
    "Q13765" "Q99733" "Q9H0A0" "P42695" "Q6IBW4" "Q09161" "Q9HCD5" "Q8NEJ9" "P55769" "O15226"
    "Q9BVI4" "Q9H6R4" "Q14978" "P78316" "Q9Y3C1" "P46087" "O00567" "Q9Y2X3" "Q86U38" "O95478"
    "Q08J23" "Q96P11" "O43809" "Q14980" "P57740" "Q8WUM0" "O75694" "Q12769" "Q92621" "Q8TEM1"
    "Q8N1F7" "P52948" "O15381" "Q9UBU9" "Q5BJF6" "P11940" "Q15102" "P09874" "Q9HBE1" "Q86U86"
    "P12004" "Q14690" "Q9NR12" "Q8IZL8" "O00541" "P17858" "P15259" "Q96HS1" "P35232" "Q99623"
    "Q8IWS0" "Q15149" "O43660" "Q9H307" "Q7Z3K3" "P28340" "Q9BY77" "Q07864" "O95602" "P24928"
    "P30876" "O14802" "Q8NEY8" "P62136" "P36873" "P30153" "P60510" "O14744" "Q9UMS4" "Q8WWY3"
    "O43172" "O94906" "Q6P2Q9" "P17980" "O43242" "Q8WXF1" "P26599" "Q15269" "P32322" "P62820"
    "Q92878" "Q9UKM9" "P62826" "P49792" "P61224" "P54136" "Q8IY67" "Q09028" "P98175" "Q9NW64"
    "P49756" "Q9P2N5" "Q9NW13" "Q9P258" "Q9Y2P8" "P46063" "P35250" "P35249" "Q5UIP0" "O15541"
    "Q99496" "Q5VTR2" "Q15287" "O95758" "P78424" "Q9H7B2" "Q07020" "Q02543" "P35268" "P61254"
    "P46776" "P47914" "P49207" "Q9Y3U8" "P46777" "Q02878" "P18124" "P05386" "P05387" "P46783"
    "P25398" "P62269" "Q86WX3" "P62266" "P62847" "P62081" "P62241" "Q5JTH9" "Q14684" "O43818"
    "Q15050" "O43290" "Q15020" "Q9UQR0" "Q6P3W7" "Q9NVU7" "Q9UGP8" "Q9H4L4" "Q15459" "Q12874"
    "O75533" "Q15393" "P23246" "Q9H9B4" "Q96ST3" "Q15477" "P42285" "O75746" "Q9UJS0" "P12235"
    "Q9NWH9" "O95391" "P28370" "P51532" "O60264" "Q92922" "Q92925" "Q14683" "Q9UQE7" "Q96SB8"
    "A6NHR9" "O75643" "Q96DI7" "P08621" "P62316" "P62318" "P62304" "P63162" "Q13573" "P18583"
    "Q9HB58" "Q8N5C6" "P37108" "Q9UHB9" "O76094" "Q96SB4" "Q8IYB3" "Q9UQ35" "Q07955" "O75494"
    "Q05519" "Q13243" "Q13247" "Q16629" "Q13242" "Q08945" "Q9Y3F4" "O00267" "Q7KZ85" "O75683"
    "P26639" "Q12788" "O14776" "Q13428" "Q9NXF1" "Q9UBB9" "Q8NI27" "Q13769" "Q9Y2W1" "P12270"
    "P62995" "Q14669" "Q7L0Y3" "Q7Z2T5" "Q9UJA5" "Q8WWH5" "Q2NL82" "Q15361" "P68363" "P68366"
    "Q01081" "P26368" "O15042" "O95071" "O60701" "Q96T88" "Q92900" "Q9BZI7" "Q8NFA0" "Q53GS9"
    "Q9BVJ6" "Q8TED0" "Q9Y5J1" "O75691" "Q9BRU9" "Q9NYH9" "P21796" "Q99986" "Q9Y2W2" "Q9GZL7"
    "Q8NI36" "O15213" "Q9NNW5" "Q96S55" "Q9HCS7" "Q9HAV4" "P18887" "P12956" "Q8IZH2" "Q9H0D6"
    "Q9H6S0" "Q9Y5A9" "P61981" "P27348" "P63104" "O75152" "Q8WU90" "Q7Z2W4" "Q96KR1" "Q5BKZ1"
    "Q9UL40" "Q14966"
)

# Counters
TOTAL=${#ACCESSIONS[@]}
SUCCESS=0
FAILED=0
SKIPPED=0

echo "Starting download of $TOTAL protein accessions..."

# Function to log messages
log_message() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message" | tee -a "$LOG_FILE"
}

log_error() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] ERROR: $message" | tee -a "$ERROR_LOG" >> "$LOG_FILE"
}

# Download each accession
for accession in "${ACCESSIONS[@]}"; do
    echo "Processing: $accession"
    
    # Source and destination paths
    SOURCE_PATH="embl/alphapulldown/input_features/Homo_sapiens/${accession}.pkl.xz"
    DEST_PATH="${DEST_DIR}/${accession}.pkl.xz"
    
    # Check if file already exists
    if [[ -f "$DEST_PATH" ]]; then
        log_message "File already exists, skipping: $accession"
        ((SKIPPED++))
        continue
    fi
    
    # Download the file
    echo "Downloading: $accession"
    if mc cp "$SOURCE_PATH" "$DEST_PATH" 2>/dev/null; then
        # Verify download was successful
        if [[ -f "$DEST_PATH" && -s "$DEST_PATH" ]]; then
            log_message "SUCCESS: Downloaded $accession"
            ((SUCCESS++))
        else
            log_error "Download failed - file missing or empty: $accession"
            rm -f "$DEST_PATH" 2>/dev/null
            ((FAILED++))
        fi
    else
        log_error "Download failed: $accession"
        ((FAILED++))
    fi
    
    # Small delay between downloads
    sleep 0.5
done

# Summary
echo ""
echo "=== DOWNLOAD SUMMARY ==="
echo "Total accessions: $TOTAL"
echo "Successfully downloaded: $SUCCESS"
echo "Skipped (already exists): $SKIPPED"
echo "Failed: $FAILED"

if [[ $FAILED -gt 0 ]]; then
    echo ""
    echo "Some downloads failed. Check $ERROR_LOG for details."
    echo "You can re-run this script to retry failed downloads."
    exit 1
else
    echo ""
    echo "All downloads completed successfully!"
    exit 0
fi 