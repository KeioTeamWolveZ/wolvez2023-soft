#include <linux/build-salt.h>
#include <linux/module.h>
#include <linux/vermagic.h>
#include <linux/compiler.h>

BUILD_SALT;

MODULE_INFO(vermagic, VERMAGIC_STRING);
MODULE_INFO(name, KBUILD_MODNAME);

__visible struct module __this_module
__attribute__((section(".gnu.linkonce.this_module"))) = {
	.name = KBUILD_MODNAME,
	.init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
	.exit = cleanup_module,
#endif
	.arch = MODULE_ARCH_INIT,
};

#ifdef CONFIG_RETPOLINE
MODULE_INFO(retpoline, "Y");
#endif

static const struct modversion_info ____versions[]
__used
__attribute__((section("__versions"))) = {
	{ 0x9b929f65, "module_layout" },
	{ 0x3ce4ca6f, "disable_irq" },
	{ 0xf9a482f9, "msleep" },
	{ 0xb7700415, "param_ops_int" },
	{ 0x2e5810c6, "__aeabi_unwind_cpp_pr1" },
	{ 0x6e1698a, "hrtimer_active" },
	{ 0x1f1e05af, "hrtimer_forward" },
	{ 0x4998222d, "hrtimer_cancel" },
	{ 0x47229b5c, "gpio_request" },
	{ 0x9b688965, "gpio_to_desc" },
	{ 0xb43f9365, "ktime_get" },
	{ 0xb1ad28e0, "__gnu_mcount_nc" },
	{ 0xfb0ed07b, "tty_register_driver" },
	{ 0x67ea780, "mutex_unlock" },
	{ 0x626ce107, "put_tty_driver" },
	{ 0xccfc0a6d, "tty_set_operations" },
	{ 0x4a16dd15, "hrtimer_start_range_ns" },
	{ 0x5c732fab, "__tty_insert_flip_char" },
	{ 0xe346f67a, "__mutex_init" },
	{ 0x7c32d0f0, "printk" },
	{ 0xe7eed781, "tty_port_init" },
	{ 0xc271c3be, "mutex_lock" },
	{ 0x7583f8d1, "gpiod_direction_input" },
	{ 0xc68abf5f, "gpiod_direction_output_raw" },
	{ 0xd6b8e852, "request_threaded_irq" },
	{ 0x2196324, "__aeabi_idiv" },
	{ 0x14a394f8, "gpiod_set_debounce" },
	{ 0x67b27ec1, "tty_std_termios" },
	{ 0x92ba339d, "tty_unregister_driver" },
	{ 0x3d73d4, "__tty_alloc_driver" },
	{ 0xfe990052, "gpio_free" },
	{ 0x409873e3, "tty_termios_baud_rate" },
	{ 0xfcec0987, "enable_irq" },
	{ 0x64a1ad16, "tty_port_link_device" },
	{ 0x7bac717f, "gpiod_to_irq" },
	{ 0x9a8d7dc4, "gpiod_set_raw_value" },
	{ 0x5b586cbc, "hrtimer_init" },
	{ 0x91e3f12c, "tty_flip_buffer_push" },
	{ 0x6e661f49, "gpiod_get_raw_value" },
	{ 0xc1514a3b, "free_irq" },
};

static const char __module_depends[]
__used
__attribute__((section(".modinfo"))) =
"depends=";


MODULE_INFO(srcversion, "4C4A4CAE15187589FCCEF4B");
