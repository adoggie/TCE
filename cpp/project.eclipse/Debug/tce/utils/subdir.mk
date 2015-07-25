################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
CPP_SRCS += \
/Users/socketref/Desktop/projects/dvr/ply/code/cpp/tce/utils/plainconfig.cpp 

OBJS += \
./tce/utils/plainconfig.o 

CPP_DEPS += \
./tce/utils/plainconfig.d 


# Each subdirectory must supply rules for building sources it contributes
tce/utils/plainconfig.o: /Users/socketref/Desktop/projects/dvr/ply/code/cpp/tce/utils/plainconfig.cpp
	@echo 'Building file: $<'
	@echo 'Invoking: Cross G++ Compiler'
	g++ -I/opt/local/include -O0 -g3 -Wall -c -fmessage-length=0 -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


