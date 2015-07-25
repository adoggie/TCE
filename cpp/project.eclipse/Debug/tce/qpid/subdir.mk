################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
CPP_SRCS += \
/Users/socketref/Desktop/projects/dvr/ply/code/cpp/tce/qpid/qpid_adapter.cpp \
/Users/socketref/Desktop/projects/dvr/ply/code/cpp/tce/qpid/qpid_conn.cpp 

OBJS += \
./tce/qpid/qpid_adapter.o \
./tce/qpid/qpid_conn.o 

CPP_DEPS += \
./tce/qpid/qpid_adapter.d \
./tce/qpid/qpid_conn.d 


# Each subdirectory must supply rules for building sources it contributes
tce/qpid/qpid_adapter.o: /Users/socketref/Desktop/projects/dvr/ply/code/cpp/tce/qpid/qpid_adapter.cpp
	@echo 'Building file: $<'
	@echo 'Invoking: Cross G++ Compiler'
	g++ -I/opt/local/include -O0 -g3 -Wall -c -fmessage-length=0 -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '

tce/qpid/qpid_conn.o: /Users/socketref/Desktop/projects/dvr/ply/code/cpp/tce/qpid/qpid_conn.cpp
	@echo 'Building file: $<'
	@echo 'Invoking: Cross G++ Compiler'
	g++ -I/opt/local/include -O0 -g3 -Wall -c -fmessage-length=0 -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


