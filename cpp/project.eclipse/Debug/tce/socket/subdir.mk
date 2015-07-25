################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
CPP_SRCS += \
/Users/socketref/Desktop/projects/dvr/ply/code/cpp/tce/socket/sock_adapter.cpp \
/Users/socketref/Desktop/projects/dvr/ply/code/cpp/tce/socket/sock_conn.cpp 

OBJS += \
./tce/socket/sock_adapter.o \
./tce/socket/sock_conn.o 

CPP_DEPS += \
./tce/socket/sock_adapter.d \
./tce/socket/sock_conn.d 


# Each subdirectory must supply rules for building sources it contributes
tce/socket/sock_adapter.o: /Users/socketref/Desktop/projects/dvr/ply/code/cpp/tce/socket/sock_adapter.cpp
	@echo 'Building file: $<'
	@echo 'Invoking: Cross G++ Compiler'
	g++ -I/opt/local/include -O0 -g3 -Wall -c -fmessage-length=0 -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '

tce/socket/sock_conn.o: /Users/socketref/Desktop/projects/dvr/ply/code/cpp/tce/socket/sock_conn.cpp
	@echo 'Building file: $<'
	@echo 'Invoking: Cross G++ Compiler'
	g++ -I/opt/local/include -O0 -g3 -Wall -c -fmessage-length=0 -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


