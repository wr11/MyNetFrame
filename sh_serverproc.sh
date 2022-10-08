#!/bin/bash

MONGO=/home/oceanmongos/mongodb-linux-x86_64-4.0.19/bin/mongo
MONGO_DB=db_1
MONGO_USER=db_1
MONGO_PWD=123456

ROOT_PATH=$(cd `dirname $0`/..; pwd)
SERVER_PATH=${ROOT_PATH}/qz_server

BOOT=${SERVER_PATH}/src/Boot.lua
CONF=${SERVER_PATH}/conf/Conf.json
ARGS="${BOOT} ${ROOT_PATH} ${CONF}"
CMD=./tcstart


VAR_PATH=${SERVER_PATH}/var
LOG_PATH=${SERVER_PATH}/log

LGS_LOG=${LOG_PATH}/lgs.log
GBS_LOG=${LOG_PATH}/gbs.log
DBS_LOG=${LOG_PATH}/dbs.log
GAS_LOG=${LOG_PATH}/gas.log
GATE_LOG=${LOG_PATH}/gate.log
HTTPC_LOG=${LOG_PATH}/httpc.log

CMS_LOG=${LOG_PATH}/cms.log
TMS_LOG=${LOG_PATH}/tms.log
SMS_LOG=${LOG_PATH}/sms.log
SCS_LOG=${LOG_PATH}/scs.log
HTTPD_LOG=${LOG_PATH}/httpd.log

BAK_PATH=${LOG_PATH}/bak/$(date +%Y%m%d%H%M%S)

MAX_NUM=9

START_OK="<!--XSUPERVISOR:BEGIN-->SUCCESSFUL<!--XSUPERVISOR:END-->"
SHUTDOWN_OK="<!--XSUPERVISOR:BEGIN-->GAME SAVED<!--XSUPERVISOR:END-->"


fun_db() {
	db=$1
	user=$2
	pwd=$3
	${MONGO} "mongodb://g119mongo:g119mongo163@10.212.5.114:30000/${db}?authSource=admin" --eval "if (db.getUser('${user}') == null) {db.createUser({user:'${user}', pwd:'${pwd}', roles:[{role:'readWrite', db:'${db}'}]})}"
}

fun_init() {
	fun_db ${MONGO_DB} ${MONGO_USER} ${MONGO_PWD}
	cat ${SERVER_PATH}/conf/Conf.json.sample | grep -v bUseBp | grep -v bUseCmd > ${SERVER_PATH}/conf/Conf.json
	chmod +x ${SERVER_PATH}/tcstart
}

fun_start_cross() {
	cd ${SERVER_PATH}
	mkdir -p ${LOG_PATH}
	mkdir -p ${BAK_PATH}
	mkdir -p ${VAR_PATH}

	for app in cms tms sms scs httpd
	do
		for loop in $(seq 1 ${MAX_NUM})
		do
			if [[ $(ps -ef | grep -v "grep" | grep "${ARGS} ${app}_${loop}") != "" ]]
			then
				echo "【错误】 ${app}_${loop}进程还在运行中，不能重复启动，请先确认关闭！"
				exit
			fi
		done
	done

	mv ${CMS_LOG} ${TMS_LOG} ${SMS_LOG} ${SCS_LOG} ${HTTPD_LOG} ${BAK_PATH}/

#	nohup ${CMD} ${ARGS} tms_1 >> ${TMS_LOG} 2>&1 &
#	nohup ${CMD} ${ARGS} sms_1 >> ${SMS_LOG} 2>&1 &
#	nohup ${CMD} ${ARGS} scs_1 >> ${SCS_LOG} 2>&1 &
#	nohup ${CMD} ${ARGS} scs_2 >> ${SCS_LOG} 2>&1 &
	for app in cms tms sms scs httpd
	do
		for loop in $(seq 1 ${MAX_NUM})
		do
			if [[ $(cat ${CONF} | grep -v "//" | grep "${app}_${loop}") != "" ]]
			then
				nohup ${CMD} ${ARGS} "${app}_${loop}" >> "${LOG_PATH}/${app}.log" 2>&1 &
			fi
		done
	done
}

fun_start_game() {
	cd ${SERVER_PATH}
	mkdir -p ${LOG_PATH}
	mkdir -p ${BAK_PATH}
	mkdir -p ${VAR_PATH}

	for app in dbs lgs httpc gbs gas gate
	do
		for loop in $(seq 1 ${MAX_NUM})
		do
			if [[ $(ps -ef | grep -v "grep" | grep "${ARGS} ${app}_${loop}") != "" ]]
			then
				echo "【错误】 ${app}_${loop}进程还在运行中，不能重复启动，请先确认关闭！"
				exit
			fi
		done
	done

	mv ${LGS_LOG} ${GBS_LOG} ${DBS_LOG} ${GAS_LOG} ${GATE_LOG} ${HTTPC_LOG} ${BAK_PATH}/

#	nohup ${CMD} ${ARGS} dbs_1 >> ${DBS_LOG} 2>&1 &
#	nohup ${CMD} ${ARGS} dbs_2 >> ${DBS_LOG} 2>&1 &
#	nohup ${CMD} ${ARGS} lgs_1 >> ${LGS_LOG} 2>&1 &
#	nohup ${CMD} ${ARGS} gbs_1 >> ${GBS_LOG} 2>&1 &
#	nohup ${CMD} ${ARGS} gas_1 >> ${GAS_LOG} 2>&1 &
#	nohup ${CMD} ${ARGS} gas_2 >> ${GAS_LOG} 2>&1 &
#	nohup ${CMD} ${ARGS} gate_1 >> ${GATE_LOG} 2>&1 &
#	nohup ${CMD} ${ARGS} gate_2 >> ${GATE_LOG} 2>&1 &

	for app in dbs lgs httpc gbs gas gate
	do
		for loop in $(seq 1 ${MAX_NUM})
		do
			if [[ $(cat ${CONF} | grep -v "//" | grep "${app}_${loop}") != "" ]]
			then
				nohup ${CMD} ${ARGS} "${app}_${loop}" >> "${LOG_PATH}/${app}.log" 2>&1 &
			fi
		done
	done

}

fun_start() {
	fun_start_cross
	fun_start_game
}

fun_shutdown_cross() {
	for app in httpd scs sms tms cms
	do
		for loop in $(seq 1 ${MAX_NUM})
		do
			if [[ $(ps -ef | grep -v "grep" | grep "${ARGS} ${app}_${loop}") != "" ]]
			then
				# 00${loop}] 匹配 nAppId
				if [[ $(cat ${LOG_PATH}/${app}.log | grep -E "${START_OK}" | grep -E "\[[4-9][0-9]0${loop}") == "" ]]
				then
					echo "【错误】 ${app}_${loop}进程还没启动成功，暂时无法关闭（或者强制kill掉进程）！"
					exit
				fi

				ps -ef | grep "${ARGS} ${app}_${loop}" | grep -v grep | awk '{print $2}' | xargs kill
				for i in $(seq 1 30)
				do
					if [[ $(ps -ef | grep -v "grep" | grep "${ARGS} ${app}_${loop}") != "" ]]
					then
						echo "shutdown ${app}_${loop} sleep ${i}s"
						sleep 1s
					fi
				done
				if [[ $(ps -ef | grep -v "grep" | grep "${ARGS} ${app}_${loop}") != "" ]]
				then
					echo "【错误】 ${app}_${loop}进程关闭失败！"
					exit
				fi
			fi
		done
	done
#	ps -ef | grep "${ARGS} tms_1" | grep -v grep | awk '{print $2}' | xargs kill
#	ps -ef | grep "${ARGS} sms_1" | grep -v grep | awk '{print $2}' | xargs kill
#	ps -ef | grep "${ARGS} scs_1" | grep -v grep | awk '{print $2}' | xargs kill
#	ps -ef | grep "${ARGS} scs_2" | grep -v grep | awk '{print $2}' | xargs kill

	echo ${CMS_LOG} ; cat ${CMS_LOG} | grep -A 100 "Boot.shutdown"
	echo ${TMS_LOG} ; cat ${TMS_LOG} | grep -A 100 "Boot.shutdown"
	echo ${SMS_LOG} ; cat ${SMS_LOG} | grep -A 100 "Boot.shutdown"
	echo ${SCS_LOG} ; cat ${SCS_LOG} | grep -A 100 "Boot.shutdown"
	echo ${HTTPD_LOG} ; cat ${HTTPD_LOG} | grep -A 100 "Boot.shutdown"

}

fun_shutdown_game() {
	for app in gate gas gbs httpc lgs dbs
	do
		for loop in $(seq 1 ${MAX_NUM})
		do
			if [[ $(ps -ef | grep -v "grep" | grep "${ARGS} ${app}_${loop}") != "" ]]
			then
				# \[1[0-9]0${loop} 匹配 nAppId
				if [[ $(cat ${LOG_PATH}/${app}.log | grep -E "${START_OK}" | grep "\[[1-3][0-9]0${loop}") == "" ]]
				then
					echo "【错误】 ${app}_${loop}进程还没启动成功，暂时无法关闭（或者强制kill掉进程）！"
					exit
				fi

				ps -ef | grep "${ARGS} ${app}_${loop}" | grep -v grep | awk '{print $2}' | xargs kill
				for i in $(seq 1 30)
				do
					if [[ $(ps -ef | grep -v "grep" | grep "${ARGS} ${app}_${loop}") != "" ]]
					then
						echo "shutdown ${app}_${loop} sleep ${i}s"
						sleep 1s
					fi
				done
				if [[ $(ps -ef | grep -v "grep" | grep "${ARGS} ${app}_${loop}") != "" ]]
				then
					echo "【错误】 ${app}_${loop}进程关闭失败！"
					exit
				fi
			fi
		done
	done

#	ps -ef | grep "${ARGS} gate_1" | grep -v grep | awk '{print $2}' | xargs kill
#	ps -ef | grep "${ARGS} gate_2" | grep -v grep | awk '{print $2}' | xargs kill
#	ps -ef | grep "${ARGS} gas_1" | grep -v grep | awk '{print $2}' | xargs kill
#	ps -ef | grep "${ARGS} gas_2" | grep -v grep | awk '{print $2}' | xargs kill
#	sleep 1s
#	ps -ef | grep "${ARGS} gbs_1" | grep -v grep | awk '{print $2}' | xargs kill
#	ps -ef | grep "${ARGS} lgs_1" | grep -v grep | awk '{print $2}' | xargs kill
#	sleep 1s
#	ps -ef | grep "${ARGS} dbs_1" | grep -v grep | awk '{print $2}' | xargs kill
#	ps -ef | grep "${ARGS} dbs_2" | grep -v grep | awk '{print $2}' | xargs kill

	echo ${HTTPC_LOG} ; cat ${HTTPC_LOG} | grep -A 100 "Boot.shutdown"
	echo ${GATE_LOG} ; cat ${GATE_LOG} | grep -A 100 "Boot.shutdown"
	echo ${GAS_LOG} ; cat ${GAS_LOG} | grep -A 100 "Boot.shutdown"
	echo ${GBS_LOG} ; cat ${GBS_LOG} | grep -A 100 "Boot.shutdown"
	echo ${LGS_LOG} ; cat ${LGS_LOG} | grep -A 100 "Boot.shutdown"
	echo ${DBS_LOG} ; cat ${DBS_LOG} | grep -A 100 "Boot.shutdown"
}

fun_shutdown() {
	fun_shutdown_game
	fun_shutdown_cross
}

fun_log_cross() {
	echo ${CMS_LOG} ; cat ${CMS_LOG}
	echo ${TMS_LOG} ; cat ${TMS_LOG}
	echo ${SMS_LOG} ; cat ${SMS_LOG}
	echo ${SCS_LOG} ; cat ${SCS_LOG}
	echo ${HTTPD_LOG} ; cat ${HTTPD_LOG}
}

fun_log_game() {
	echo ${DBS_LOG} ; cat ${DBS_LOG}
	echo ${LGS_LOG} ; cat ${LGS_LOG}
	echo ${GBS_LOG} ; cat ${GBS_LOG}
	echo ${GAS_LOG} ; cat ${GAS_LOG}
	echo ${GATE_LOG} ; cat ${GATE_LOG}
	echo ${HTTPC_LOG} ; cat ${HTTPC_LOG}
}

fun_log() {
	fun_log_cross
	fun_log_game
}

fun_status() {
	ps -ef | grep "${ARGS}" | grep -v grep
}

fun_kill() {
	echo "[$(date +%Y%m%d%H%M%S)][$(whoami)] kill -9 ${ARGS}" >> "${LOG_PATH}/kill.log"
	ps -ef | grep "${ARGS}" | grep -v grep | awk '{print $2}' | xargs kill -9
}

# 这里的参数是/usr/share/zoneinfo下的相对路径
fun_zdump() {
	zoneinfo=$1
	zonefile="${ROOT_PATH}/qz_pub/zoneinfo/${zoneinfo}.lua"
	mkdir -p $(dirname ${zonefile})

	echo -e "return {" > ${zonefile}
	zdump -c 1970,2500 -v "/usr/share/zoneinfo/${zoneinfo}" | \
		grep gmtoff | \
		awk -F ' ' '{printf "{{%s,%s,%2s,%s,%s,%s}, {%s,%s,%2s,%s,%s,%s}, %s, %s},\n", $6,$3,$4,substr($5,1,2),substr($5,4,2),substr($5,7,2), $13,$10,$11,substr($12,1,2),substr($12,4,2),substr($12,7,2),  substr($15,7), substr($16,8)}' >> ${zonefile}
	echo "}" >> ${zonefile}
	sed -i 's/Jan/ 1/g' ${zonefile}
	sed -i 's/Feb/ 2/g' ${zonefile}
	sed -i 's/Mar/ 3/g' ${zonefile}
	sed -i 's/Apr/ 4/g' ${zonefile}
	sed -i 's/May/ 5/g' ${zonefile}
	sed -i 's/Jun/ 6/g' ${zonefile}
	sed -i 's/Jul/ 7/g' ${zonefile}
	sed -i 's/Aug/ 8/g' ${zonefile}
	sed -i 's/Sep/ 9/g' ${zonefile}
	sed -i 's/Oct/10/g' ${zonefile}
	sed -i 's/Nov/11/g' ${zonefile}
	sed -i 's/Dec/12/g' ${zonefile}

	echo "请提交最终生成lua时区数据表：${zonefile}"
}

## 命令行帮助
fun_help() {
cat <<EOF
Usage:
	$0 init					   # 初始化数据库和配置
	$0 start					  # 启动所有服务进程
	$0 start_cross				# 启动跨服服务进程
	$0 start_game				 # 启动区服服务进程
	$0 shutdown				   # 关闭所有服务进程
	$0 shutdown_cross			 # 关闭跨服服务进程
	$0 shutdown_game			  # 关闭区服服务进程
	$0 status					 # 查看所有服务状态
	$0 log						# 查看所有服务日志
	$0 kill					   # 强制杀掉所有进程
	$0 zdump [zoneinfo]		   % 转换linux时区数据库文件
	$0 db [db user pwd]		   # 创建mongo用户和数据库索引
EOF
}

case $# in
	1)
		case $1 in
			init) fun_init ; exit $? ;;
			start) fun_start ; exit $? ;;
			start_cross) fun_start_cross ; exit $? ;;
			start_game) fun_start_game ; exit $? ;;
			status) fun_status ; exit $? ;;
			log) fun_log ; exit $? ;;
			kill) fun_kill ; exit $? ;;
			shutdown) fun_shutdown ; exit $? ;;
			shutdown_cross) fun_shutdown_cross ; exit $? ;;
			shutdown_game) fun_shutdown_game ; exit $? ;;

			*) fun_help; exit 1 ;;
		esac
	;;
	2)
		case $1 in
			zdump) fun_zdump $2 ; exit $? ;;

			*) fun_help; exit 1 ;;
		esac
	;;
	4)
		case $1 in
			db) fun_db $2 $3 $4 ; exit $? ;;

			*) fun_help; exit 1 ;;
		esac
	;;
	*)
		case $1 in
			*)  fun_help ; exit 1 ;;
		esac
	;;
esac
